import logging
import re
from time import monotonic
from typing import Any

from .config import settings
from .cypher_generator import generate_read_query
from .db import read
from .entity_resolution import best_candidate_for_intent
from .graph_builder import build_graph
from .graph_schema import DEFAULT_LIMIT
from .intent_detector import detect_intent
from .intent_models import QueryTrace
from .llm import explain
from .query_execution import execute_generated_read_query
from .query_templates import QUERY_TEMPLATES
from .schema_context import ALLOWED_LABELS, TEMPLATE_INTENTS, TERM_INTENTS

logger = logging.getLogger("super_bank.service")

_CATALOG_CACHE: list[dict[str, Any]] = []
_CATALOG_CACHED_AT = 0.0

CONCEPTS = {
    "dataset": {
        "template": "concept_dataset",
        "answer": "A dataset is a governed collection of information consumed by a business process or system. In this graph, datasets record data lineage from source integration to payment, compliance and settlement usage.",
    },
    "system": {
        "template": "concept_system",
        "answer": "A system is a managed technology asset. In this graph each operational system can have a managing team, an employee IT owner, an employee business owner, users, access governance and regulatory relationships.",
    },
    "business process": {
        "template": "concept_business_process",
        "answer": "A business process is an operational flow made of ordered steps. The payment lifecycle includes compliance decision, payment release, settlement and automatic status update.",
    },
    "data pipeline": {
        "template": "concept_data_pipeline",
        "answer": "A data pipeline carries validated information from a source system such as Input Hub into datasets consumed by operational or compliance systems.",
    },
}

def _definition_concept(question: str) -> str | None:
    q = re.sub(r"[^a-z0-9 ]+", " ", question.lower())
    q = re.sub(r"\s+", " ", q).strip()
    match = re.match(r"^(?:what is|what s|define|explain)\s+(?:a |an |the )?(dataset|system|business process|data pipeline)s?\s*$", q)
    return match.group(1) if match else None

def _catalog() -> list[dict[str, Any]]:
    global _CATALOG_CACHE, _CATALOG_CACHED_AT
    now = monotonic()
    if _CATALOG_CACHE and now - _CATALOG_CACHED_AT < settings.entity_catalog_cache_seconds:
        return _CATALOG_CACHE
    _CATALOG_CACHE = read(QUERY_TEMPLATES["entity_catalog"], {"labels": sorted(ALLOWED_LABELS), "limit": 1000})
    _CATALOG_CACHED_AT = now
    return _CATALOG_CACHE

def _global_rows(term: str) -> list[dict[str, Any]]:
    return read(QUERY_TEMPLATES["global_search"], {"labels": sorted(ALLOWED_LABELS), "term": term, "limit": DEFAULT_LIMIT})

def _clean_term(term: str | None) -> str | None:
    if term is None:
        return None
    cleaned = re.sub(r"\s+", " ", str(term)).strip()
    return cleaned or None


def _params(intent: str, term: str | None) -> dict[str, Any]:
    params: dict[str, Any] = {"limit": DEFAULT_LIMIT}
    if intent in TERM_INTENTS:
        cleaned = _clean_term(term)
        if not cleaned:
            raise ValueError(f"Intent {intent!r} requires a non-empty resolved term.")
        params["term"] = cleaned
    return params

def _concept_response(concept: str) -> dict[str, Any]:
    definition = CONCEPTS[concept]
    rows = read(QUERY_TEMPLATES[definition["template"]], {"limit": 30})
    trace = QueryTrace(
        query_method="fast_concept_definition",
        template=definition["template"],
        interpreted_intent="overview",
        confidence=1.0,
        resolved_term=concept.title(),
    )
    return {
        "intent": "overview",
        "answer": definition["answer"],
        "rows": rows,
        "graph": build_graph(rows),
        "llm_status": "not_called_fast_path",
        "query_trace": trace.model_dump(),
    }

def answer_question(question: str) -> dict[str, Any]:
    concept = _definition_concept(question)
    if concept:
        return _concept_response(concept)

    catalog = _catalog()
    decision, candidates = detect_intent(question, catalog)
    selected_candidate = best_candidate_for_intent(decision.intent, candidates)
    resolved_term = _clean_term(decision.term)
    if selected_candidate and decision.intent in {"system_impact", "system_owners", "process_pipeline", "next_step", "employee_search", "employee_responsibilities"}:
        resolved_term = _clean_term(selected_candidate.name)

    trace = QueryTrace(
        query_method="pending",
        template=None,
        interpreted_intent=decision.intent,
        confidence=decision.confidence,
        corrected_question=decision.corrected_question,
        resolved_term=resolved_term,
        entity_candidates=candidates,
    )
    rows: list[dict[str, Any]] = []

    if decision.intent in TEMPLATE_INTENTS:
        trace.query_method = "approved_template_v2"
        trace.template = decision.intent
        if decision.intent in TERM_INTENTS and not resolved_term:
            trace.query_method = "clarification_required_missing_term"
            trace.fallback_reason = (
                f"Intent '{decision.intent}' requires a named graph entity, but no target was resolved. "
                "No broad empty-term query was executed."
            )
            logger.warning(
                "question.missing_required_term intent=%s question=%r candidates=%r",
                decision.intent,
                question[:160],
                [candidate.name for candidate in candidates],
            )
        else:
            rows = read(QUERY_TEMPLATES[decision.intent], _params(decision.intent, resolved_term))
            if not rows and settings.global_search_enabled and resolved_term and decision.intent not in {"kpis", "overview"}:
                trace.fallback_reason = f"Approved v2 template '{decision.intent}' returned no evidence."
                rows = _global_rows(resolved_term)
                if rows:
                    trace.query_method = "global_search_after_empty_template"
                    trace.template = "global_search"

    elif decision.intent == "global_search":
        trace.query_method = "global_search"
        trace.template = "global_search"
        rows = _global_rows(resolved_term or question)

    elif decision.intent == "clarification_required":
        trace.query_method = "clarification_with_related_evidence"
        trace.fallback_reason = decision.reason
        if resolved_term:
            rows = _global_rows(resolved_term)

    elif decision.intent == "generated_read_query" and settings.generated_cypher_enabled:
        trace.query_method = "validated_generated_read"
        plan = generate_read_query(question, candidates)
        if plan:
            rows, validation = execute_generated_read_query(plan)
            trace.generated_query_validation = validation.reasons
            if settings.expose_generated_cypher and validation.valid:
                trace.generated_cypher = plan.cypher
        if not rows:
            trace.fallback_reason = "Validated generated query did not return evidence."
            fallback = resolved_term or (candidates[0].name if candidates else question)
            rows = _global_rows(fallback)
            if rows:
                trace.query_method = "global_search_after_generated_query"
                trace.template = "global_search"

    if not rows and settings.generated_cypher_enabled and decision.intent not in {"kpis", "missing_owners", "clarification_required", "generated_read_query"}:
        plan = generate_read_query(question, candidates)
        if plan:
            generated_rows, validation = execute_generated_read_query(plan)
            trace.generated_query_validation = validation.reasons
            if settings.expose_generated_cypher and validation.valid:
                trace.generated_cypher = plan.cypher
            if generated_rows:
                rows = generated_rows
                trace.query_method = "validated_generated_read_after_empty_retrieval"
                trace.template = None

    payload = trace.model_dump()
    answer, llm_status = explain(question, rows, payload)
    logger.info("question.answered model=v2 intent=%s method=%s rows=%d term=%r", decision.intent, trace.query_method, len(rows), resolved_term)
    return {
        "intent": decision.intent,
        "answer": answer,
        "rows": rows,
        "graph": build_graph(rows),
        "llm_status": llm_status,
        "query_trace": payload,
    }
