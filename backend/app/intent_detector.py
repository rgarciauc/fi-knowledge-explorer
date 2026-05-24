import json
import logging
import re
from difflib import SequenceMatcher

from .config import settings
from .entity_resolution import best_candidate_for_intent, find_entity_candidates, meaningful_tokens, normalize
from .intent_models import EntityCandidate, IntentDecision
from .ollama_client import structured_generate
from .schema_context import INTENT_DESCRIPTION, SCHEMA_PROMPT


logger = logging.getLogger("super_bank.intent")


def _has_similar_word(question: str, targets: tuple[str, ...], threshold: float = 0.81) -> bool:
    tokens = normalize(question).split()
    for token in tokens:
        for target in targets:
            if token == target or SequenceMatcher(None, token, target).ratio() >= threshold:
                return True
    return False


def _extract_term_after(question: str, words: tuple[str, ...]) -> str | None:
    q = question.strip().rstrip("?.")
    lower = q.lower()
    for word in words:
        pos = lower.find(word.lower())
        if pos >= 0:
            term = q[pos + len(word):].strip(" :")
            if term:
                return term
    return None



def _department_search_term(question: str, candidates: list[EntityCandidate]) -> str:
    """Keep shared department wording broad, e.g. Compliance → both compliance departments."""
    q = normalize(question)
    removable = {
        "who", "is", "are", "working", "work", "works", "in", "the", "department",
        "departments", "employee", "employees", "staff", "people", "member", "members",
        "show", "me", "from", "belong", "belongs", "to",
    }
    tokens = [token for token in q.split() if token not in removable]
    if tokens:
        return " ".join(tokens)
    department = next((candidate for candidate in candidates if candidate.label == "Department"), None)
    return department.name if department else ""

def _deterministic_decision(question: str, candidates: list[EntityCandidate]) -> IntentDecision | None:
    q = normalize(question)
    system_candidate = next((c for c in candidates if c.label == "System"), None)

    if _has_similar_word(q, ("kpi", "kpis", "coverage", "metric", "metrics")):
        return IntentDecision(intent="kpis", confidence=0.97, reason="KPI or coverage keyword detected.")
    if "missing owner" in q or "owner gap" in q or _has_similar_word(q, ("unowned",)):
        return IntentDecision(intent="missing_owners", confidence=0.97, reason="Missing ownership wording detected.")
    if _has_similar_word(q, ("impact", "affected", "affect", "breaks", "fails", "failed", "failure", "outage", "unavailable", "down")) and system_candidate:
        return IntentDecision(
            intent="system_impact",
            term=system_candidate.name,
            target_label="System",
            confidence=max(0.84, system_candidate.score),
            corrected_question=None,
            reason="Failure/impact wording and a matching System entity were detected.",
        )
    if "next step" in q or (_has_similar_word(q, ("after",)) and any(c.label == "ProcessStep" for c in candidates)):
        candidate = next((c for c in candidates if c.label == "ProcessStep"), None)
        return IntentDecision(
            intent="next_step",
            term=candidate.name if candidate else _extract_term_after(question, ("after", "step")),
            target_label="ProcessStep",
            confidence=0.88 if candidate else 0.68,
            reason="Next-step wording detected.",
        )
    if _has_similar_word(q, ("pipeline", "steps", "workflow")) and any(c.label == "BusinessProcess" for c in candidates):
        candidate = next(c for c in candidates if c.label == "BusinessProcess")
        return IntentDecision(
            intent="process_pipeline",
            term=candidate.name,
            target_label="BusinessProcess",
            confidence=max(0.84, candidate.score),
            reason="Pipeline/workflow wording and a business process were detected.",
        )
    if _has_similar_word(q, ("owner", "owns", "owned", "accountable", "responsible")):
        candidate = next((c for c in candidates if c.label in {"System", "BusinessProcess"}), None)
        return IntentDecision(
            intent="ownership_search",
            term=candidate.name if candidate else _extract_term_after(question, ("system", "process", "for")),
            target_label=candidate.label if candidate else None,
            confidence=0.92 if candidate else 0.62,
            reason="Ownership/responsibility wording detected.",
        )
    if (
        "department" in q
        and _has_similar_word(q, ("work", "working", "works", "employee", "employees", "staff", "people", "member", "members"))
    ):
        term = _department_search_term(question, candidates)
        return IntentDecision(
            intent="department_employees",
            term=term,
            target_label="Department",
            confidence=0.94 if term else 0.70,
            reason="Department staffing wording detected; using approved department-to-employee query.",
        )
    if _has_similar_word(q, ("employee", "role", "task")):
        candidate = next((c for c in candidates if c.label == "Employee"), None)
        return IntentDecision(
            intent="employee_search",
            term=candidate.name if candidate else _extract_term_after(question, ("employee", "role", "task", "for")),
            target_label="Employee",
            confidence=0.84 if candidate else 0.62,
            reason="Employee/role/task wording detected.",
        )
    if _has_similar_word(q, ("overview", "organization", "organisation")):
        return IntentDecision(intent="overview", confidence=0.86, reason="Overview wording detected.")
    return None


def _llm_decision(question: str, candidates: list[EntityCandidate]) -> IntentDecision | None:
    candidate_json = json.dumps([candidate.model_dump() for candidate in candidates], ensure_ascii=False)
    prompt = f"""
You classify questions for a Neo4j governance knowledge graph.
Interpret paraphrases and likely typing mistakes. Never invent an entity that is not in the candidates.
Choose an approved template intent whenever it can answer the question.
Choose global_search for broad exploration around a topic/entity.
Choose generated_read_query only for genuinely complex multi-hop relationship questions not covered by a template.
Choose clarification_required if two candidate meanings are materially ambiguous.

{SCHEMA_PROMPT}

{INTENT_DESCRIPTION}

User question: {question}
Fuzzy entity candidates from the database: {candidate_json}

Return only JSON matching the supplied schema.
""".strip()
    return structured_generate("intent_detection", prompt, IntentDecision)


def _fallback_global_term(question: str, candidates: list[EntityCandidate]) -> str:
    if candidates:
        return candidates[0].name
    tokens = meaningful_tokens(question)
    return max(tokens, key=len) if tokens else question.strip()


def detect_intent(question: str, catalog: list[dict]) -> tuple[IntentDecision, list[EntityCandidate]]:
    candidates = find_entity_candidates(question, catalog)
    deterministic = _deterministic_decision(question, candidates)
    if deterministic and deterministic.confidence >= 0.84:
        logger.info(
            "intent.detected source=rules intent=%s confidence=%.2f term=%r",
            deterministic.intent,
            deterministic.confidence,
            deterministic.term,
        )
        return deterministic, candidates

    if settings.intent_detection_enabled:
        llm_decision = _llm_decision(question, candidates)
        if llm_decision and llm_decision.confidence >= settings.intent_confidence_threshold:
            matched = best_candidate_for_intent(llm_decision.intent, candidates)
            if llm_decision.intent == "department_employees":
                llm_decision.term = _department_search_term(question, candidates)
                llm_decision.target_label = "Department"
            elif matched and llm_decision.intent not in {"global_search", "generated_read_query"}:
                llm_decision.term = matched.name
                llm_decision.target_label = matched.label
            logger.info(
                "intent.detected source=ollama intent=%s confidence=%.2f term=%r",
                llm_decision.intent,
                llm_decision.confidence,
                llm_decision.term,
            )
            return llm_decision, candidates

    if deterministic:
        logger.info(
            "intent.detected source=rules_low_confidence intent=%s confidence=%.2f term=%r",
            deterministic.intent,
            deterministic.confidence,
            deterministic.term,
        )
        return deterministic, candidates

    decision = IntentDecision(
        intent="global_search",
        term=_fallback_global_term(question, candidates),
        confidence=0.52,
        reason="No high-confidence template intent was detected; using broad graph evidence retrieval.",
    )
    logger.info("intent.detected source=fallback intent=global_search term=%r", decision.term)
    return decision, candidates
