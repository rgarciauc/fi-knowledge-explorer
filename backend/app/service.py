import re
from typing import Any

from .db import read
from .graph_builder import build_graph
from .graph_schema import DEFAULT_LIMIT
from .llm import explain
from .query_templates import QUERY_TEMPLATES


def _term_after(question: str, keywords: tuple[str, ...]) -> str:
    q = question.strip().rstrip("?.")
    lower = q.lower()
    for word in keywords:
        pos = lower.find(word.lower())
        if pos >= 0:
            term = q[pos + len(word):].strip(" :")
            if term:
                return term
    return q


def _failed_system_term(question: str) -> str:
    q = question.strip().rstrip("?.")
    match = re.search(
        r"(?:if|when)\s+(?:system\s+)?(.+?)\s+(?:fails?|failed|is\s+down|goes\s+down)\b",
        q,
        flags=re.IGNORECASE,
    )
    if match:
        return match.group(1).strip()
    term = _term_after(q, ("system", "for"))
    return re.sub(r"\s+(?:fails?|failed|failure|is down|goes down)$", "", term, flags=re.I).strip()


def classify_question(question: str) -> tuple[str, dict[str, Any]]:
    q = question.lower()
    params: dict[str, Any] = {"limit": DEFAULT_LIMIT}

    if "kpi" in q or "coverage" in q:
        return "kpis", params
    if "missing owner" in q or "unowned" in q or "owner gap" in q:
        return "missing_owners", params
    if ("fail" in q or "affected" in q or "impact" in q or "down" in q) and "system" in q:
        params["term"] = _failed_system_term(question)
        return "system_impact", params
    if "next step" in q or "after" in q:
        params["term"] = _term_after(question, ("after", "step"))
        return "next_step", params
    if "pipeline" in q or "process steps" in q:
        params["term"] = _term_after(question, ("for", "pipeline", "process"))
        return "process_pipeline", params
    if "who is responsible for what" in q or "all responsibilities" in q:
        return "responsibilities_overview", params
    if "responsible" in q or "owner" in q or "owns" in q:
        params["term"] = _term_after(question, ("for", "system", "process", "owns"))
        return "ownership_search", params
    if "employee" in q or "role" in q or "task" in q:
        params["term"] = _term_after(question, ("for", "employee", "role", "task"))
        return "employee_search", params
    return "overview", params


def answer_question(question: str) -> dict[str, Any]:
    intent, params = classify_question(question)
    rows = read(QUERY_TEMPLATES[intent], params)
    answer, llm_status = explain(question, rows)
    return {
        "intent": intent,
        "answer": answer,
        "rows": rows,
        "graph": build_graph(rows),
        "llm_status": llm_status,
    }
