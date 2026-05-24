import logging
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


def _catalog() -> list[dict[str, Any]]:
    return read(
        QUERY_TEMPLATES["entity_catalog"],
        {"labels": sorted(ALLOWED_LABELS), "limit": 500},
    )


def _global_rows(term: str) -> list[dict[str, Any]]:
    return read(
        QUERY_TEMPLATES["global_search"],
        {"labels": sorted(ALLOWED_LABELS), "term": term, "limit": DEFAULT_LIMIT},
    )


def _template_params(intent: str, term: str | None) -> dict[str, Any]:
    params: dict[str, Any] = {"limit": DEFAULT_LIMIT}
    if intent in TERM_INTENTS:
        params["term"] = term or ""
    return params


def answer_question(question: str) -> dict[str, Any]:
    catalog = _catalog()
    decision, candidates = detect_intent(question, catalog)
    selected_candidate = best_candidate_for_intent(decision.intent, candidates)
    resolved_term = (
        selected_candidate.name if selected_candidate and decision.intent in TERM_INTENTS
        else decision.term
    )

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
        trace.query_method = "approved_template"
        trace.template = decision.intent
        rows = read(QUERY_TEMPLATES[decision.intent], _template_params(decision.intent, resolved_term))

        # A recognized intent with no rows should not end the interaction.
        if not rows and settings.global_search_enabled and resolved_term and decision.intent not in {"kpis", "overview"}:
            trace.fallback_reason = f"Approved template '{decision.intent}' returned no evidence."
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

    elif decision.intent == "generated_read_query":
        trace.query_method = "validated_generated_read"
        if settings.generated_cypher_enabled:
            plan = generate_read_query(question, candidates)
            if plan:
                rows, validation = execute_generated_read_query(plan)
                trace.generated_query_validation = validation.reasons
                if settings.expose_generated_cypher and validation.valid:
                    trace.generated_cypher = plan.cypher
                if not rows:
                    trace.fallback_reason = "Generated read query was rejected or returned no evidence."
            else:
                trace.fallback_reason = "Ollama did not return a valid generated query plan."
        else:
            trace.fallback_reason = "Generated Cypher is disabled by configuration."

        if not rows and settings.global_search_enabled:
            fallback_term = resolved_term or (candidates[0].name if candidates else question)
            rows = _global_rows(fallback_term)
            if rows:
                trace.query_method = "global_search_after_generated_query"
                trace.template = "global_search"

    # Last chance: generated read-only retrieval for unsolved non-administrative questions.
    if (
        not rows
        and settings.generated_cypher_enabled
        and decision.intent not in {"kpis", "missing_owners", "clarification_required", "generated_read_query"}
    ):
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
            elif not trace.fallback_reason:
                trace.fallback_reason = "No evidence was returned by templates, global search or validated read query."

    trace_payload = trace.model_dump()
    answer, llm_status = explain(question, rows, trace_payload)
    logger.info(
        "question.answered intent=%s method=%s confidence=%.2f rows=%d term=%r",
        trace.interpreted_intent,
        trace.query_method,
        trace.confidence,
        len(rows),
        trace.resolved_term,
    )
    return {
        "intent": decision.intent,
        "answer": answer,
        "rows": rows,
        "graph": build_graph(rows),
        "llm_status": llm_status,
        "query_trace": trace_payload,
    }
