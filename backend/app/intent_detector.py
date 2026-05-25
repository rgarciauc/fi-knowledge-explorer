import re
import json
import logging
from difflib import SequenceMatcher
from .config import settings
from .entity_resolution import best_candidate_for_intent, find_entity_candidates, meaningful_tokens, normalize
from .intent_models import EntityCandidate, IntentDecision
from .ollama_client import structured_generate
from .schema_context import INTENT_DESCRIPTION, SCHEMA_PROMPT

logger = logging.getLogger("super_bank.intent")

def _has_similar_word(question: str, targets: tuple[str, ...], threshold: float = 0.81) -> bool:
    tokens = normalize(question).split()
    return any(token == target or SequenceMatcher(None, token, target).ratio() >= threshold for token in tokens for target in targets)

def _extract_term_after(question: str, words: tuple[str, ...]) -> str | None:
    clean = question.strip().rstrip("?.")
    lower = clean.lower()
    for word in words:
        pos = lower.find(word.lower())
        if pos >= 0:
            term = clean[pos + len(word):].strip(" :")
            if term:
                return term
    return None

def _department_term(question: str, candidates: list[EntityCandidate]) -> str:
    removable = {"who","is","are","working","work","works","in","the","department","departments","employee","employees","staff","people","show","me","from"}
    tokens = [token for token in normalize(question).split() if token not in removable]
    if tokens:
        return " ".join(tokens)
    department = next((c for c in candidates if c.label == "Department"), None)
    return department.name if department else ""

def _term_or_candidate(question: str, candidates: list[EntityCandidate], labels: set[str], fallback_words: tuple[str, ...]) -> str:
    candidate = next((c for c in candidates if c.label in labels), None)
    return candidate.name if candidate else (_extract_term_after(question, fallback_words) or "")


def _clean_extracted_term(value: str | None) -> str | None:
    if not value:
        return None
    term = re.sub(r"\s+", " ", value).strip(" ?.:\t\n")
    return term or None


def _system_term_from_text(question: str) -> str | None:
    """Extract an explicitly named system target even when catalog/LLM resolution fails."""
    clean = re.sub(r"\s+", " ", question.strip())
    patterns = (
        r"(?i)\b(?:it\s+and\s+business\s+owners?|it\s+owner|business\s+owner|owners?|owns)\s+(?:of|for)?\s*(?:the\s+)?(?:system\s+)?(.+?)(?:\?|$)",
        r"(?i)\bif\s+(?:the\s+)?(?:system\s+)?(.+?)\s+(?:fails?|failed|is\s+unavailable|goes\s+down)\b",
        r"(?i)\b(?:impact|affected|affects?)\s+(?:of|if|by)\s+(?:the\s+)?(?:system\s+)?(.+?)(?:\?|$)",
    )
    for pattern in patterns:
        match = re.search(pattern, clean)
        if match:
            return _clean_extracted_term(match.group(1))
    return None


def _explicit_system_in_question(question: str, candidates: list[EntityCandidate]) -> EntityCandidate | None:
    """Prefer an explicitly named system over controls sharing a generic word such as Monitoring."""
    q = normalize(question)
    named_systems = [
        candidate for candidate in candidates
        if candidate.label == "System" and normalize(candidate.name) in q
    ]
    if named_systems:
        named_systems.sort(key=lambda item: len(item.name), reverse=True)
        return named_systems[0]
    return next((candidate for candidate in candidates if candidate.label == "System"), None)


def _is_impact_question(question: str) -> bool:
    q = normalize(question)
    return _has_similar_word(
        q,
        ("impact", "affected", "affect", "breaks", "fails", "failed", "failure", "outage", "unavailable", "down"),
    )

def _deterministic_decision(question: str, candidates: list[EntityCandidate]) -> IntentDecision | None:
    q = normalize(question)
    system = _explicit_system_in_question(question, candidates)
    system_term = system.name if system else _system_term_from_text(question)

    if _has_similar_word(q, ("kpi", "kpis", "coverage", "metric", "metrics")):
        return IntentDecision(intent="kpis", confidence=0.98, reason="KPI or coverage wording detected.")

    if _is_impact_question(question) and system_term:
        return IntentDecision(
            intent="system_impact",
            term=system_term,
            target_label="System",
            confidence=0.99 if normalize(system_term) in q else 0.92,
            reason="Explicit system failure/impact wording detected before broader routing.",
        )

    if ("payment" in q and _has_similar_word(q, ("flow", "journey", "lifecycle", "route", "goes", "release", "settlement", "compliance"))) or "go no go" in q:
        return IntentDecision(intent="payment_flow", confidence=0.96, reason="End-to-end payment-flow wording detected.")

    if ("team" in q or "teams" in q) and _has_similar_word(q, ("interact", "interaction", "depend", "dependency", "connect", "collaborate", "communicate")):
        return IntentDecision(intent="team_interactions", confidence=0.94, reason="Team interaction/dependency wording detected.")

    if ("it owner" in q or "business owner" in q or "owners" in q) and system_term:
        return IntentDecision(
            intent="system_owners",
            term=system_term,
            target_label="System",
            confidence=0.99 if normalize(system_term) in q else 0.92,
            reason="Named system ownership wording detected without requiring LLM fallback.",
        )

    if "department" in q and _has_similar_word(q, ("work", "working", "works", "employee", "employees", "staff", "people", "member", "members")):
        return IntentDecision(intent="department_employees", term=_department_term(question, candidates), target_label="Department", confidence=0.95, reason="Department staffing wording detected.")

    if _has_similar_word(q, ("dora", "gdpr", "regulatory", "regulation", "legal", "oversight")):
        term = "DORA" if "dora" in q else "GDPR" if "gdpr" in q else "regulatory"
        return IntentDecision(intent="regulatory_oversight", term=term, confidence=0.94, reason="Regulatory oversight wording detected.")

    if "service desk" in q or "ticket" in q or _has_similar_word(q, ("support", "incident")):
        return IntentDecision(intent="support_coverage", confidence=0.93, reason="Service-desk or ticketing wording detected.")

    if "identity" in q or _has_similar_word(q, ("access", "permission", "permissions", "entitlement")):
        return IntentDecision(intent="access_governance", confidence=0.93, reason="Access governance wording detected.")

    if "input hub" in q or _has_similar_word(q, ("feed", "feeds", "pipeline", "lineage", "external")):
        term = _term_or_candidate(question, candidates, {"System","Dataset","DataPipeline","ExternalSource"}, ("system", "dataset", "pipeline"))
        return IntentDecision(intent="data_lineage", term=term or "Input Hub", confidence=0.91, reason="Data lineage or Input Hub wording detected.")

    if "missing owner" in q or "owner gap" in q or _has_similar_word(q, ("unowned",)):
        return IntentDecision(intent="missing_owners", confidence=0.97, reason="Missing ownership wording detected.")

    if _has_similar_word(q, ("responsibility", "responsibilities", "responsible")):
        term = _term_or_candidate(question, candidates, {"Employee","Responsibility"}, ("for", "of"))
        return IntentDecision(intent="employee_responsibilities", term=term, confidence=0.84 if term else 0.66, reason="Employee responsibility wording detected.")

    if _has_similar_word(q, ("owner", "owns", "owned", "accountable")):
        term = system_term or _term_or_candidate(question, candidates, {"System","Team","Employee"}, ("system", "for"))
        return IntentDecision(
            intent="ownership_search",
            term=term,
            confidence=0.84 if term else 0.49,
            reason="General ownership wording detected.",
        )

    if "next step" in q or (_has_similar_word(q, ("after",)) and any(c.label == "ProcessStep" for c in candidates)):
        term = _term_or_candidate(question, candidates, {"ProcessStep"}, ("after", "step"))
        return IntentDecision(intent="next_step", term=term, target_label="ProcessStep", confidence=0.86 if term else 0.68, reason="Next-step wording detected.")

    if _has_similar_word(q, ("workflow", "steps", "process")) and any(c.label == "BusinessProcess" for c in candidates):
        term = _term_or_candidate(question, candidates, {"BusinessProcess"}, ("process",))
        return IntentDecision(intent="process_pipeline", term=term, target_label="BusinessProcess", confidence=0.86, reason="Process-pipeline wording detected.")

    if _has_similar_word(q, ("employee", "role", "task")):
        term = _term_or_candidate(question, candidates, {"Employee"}, ("employee", "role", "task"))
        return IntentDecision(intent="employee_search", term=term, target_label="Employee", confidence=0.82 if term else 0.62, reason="Employee wording detected.")

    if _has_similar_word(q, ("overview", "organization", "organisation", "bank")):
        return IntentDecision(intent="overview", confidence=0.85, reason="Overview wording detected.")
    return None

def _llm_decision(question: str, candidates: list[EntityCandidate]) -> IntentDecision | None:
    prompt = f"""
You classify questions for a bank technology, operations and regulatory Neo4j knowledge graph.
Interpret paraphrases and likely typing mistakes. Never invent an entity not present in candidate entities.
Prefer approved intents before generated_read_query.

{SCHEMA_PROMPT}

{INTENT_DESCRIPTION}

Question: {question}
Candidate entities: {json.dumps([c.model_dump() for c in candidates], ensure_ascii=False)}
Return only JSON matching the supplied schema.
""".strip()
    return structured_generate("intent_detection", prompt, IntentDecision)

def _fallback_term(question: str, candidates: list[EntityCandidate]) -> str:
    if candidates:
        return candidates[0].name
    tokens = meaningful_tokens(question)
    return max(tokens, key=len) if tokens else question.strip()

def detect_intent(question: str, catalog: list[dict]) -> tuple[IntentDecision, list[EntityCandidate]]:
    candidates = find_entity_candidates(question, catalog)
    deterministic = _deterministic_decision(question, candidates)
    if deterministic and deterministic.confidence >= 0.82:
        logger.info("intent.detected source=rules intent=%s confidence=%.2f term=%r", deterministic.intent, deterministic.confidence, deterministic.term)
        return deterministic, candidates

    if settings.intent_detection_enabled:
        decision = _llm_decision(question, candidates)
        if decision and decision.confidence >= settings.intent_confidence_threshold:
            matched = best_candidate_for_intent(decision.intent, candidates)
            if decision.intent == "department_employees":
                decision.term = _department_term(question, candidates)
            elif matched and decision.intent in {"system_impact","system_owners","process_pipeline","next_step","employee_search","employee_responsibilities"}:
                decision.term = matched.name
                decision.target_label = matched.label
            logger.info("intent.detected source=ollama intent=%s confidence=%.2f term=%r", decision.intent, decision.confidence, decision.term)
            return decision, candidates

    if deterministic:
        return deterministic, candidates

    decision = IntentDecision(intent="global_search", term=_fallback_term(question, candidates), confidence=0.52, reason="Using broad evidence retrieval because no approved route matched with confidence.")
    logger.info("intent.detected source=fallback intent=global_search term=%r", decision.term)
    return decision, candidates
