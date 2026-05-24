import json
from typing import Any

import httpx

from .config import settings


def explain(question: str, rows: list[dict[str, Any]]) -> tuple[str, str]:
    fallback = deterministic_answer(rows)
    if not settings.llm_enabled:
        return fallback, "disabled"
    if not rows:
        return fallback, "not_called_no_evidence"

    prompt = (
        "You are a SUPER_BANK governance assistant. Answer the user's question "
        "using only the graph evidence supplied below. Do not invent facts. "
        "State when evidence is incomplete. Use a brief, clear answer.\n\n"
        f"Question: {question}\n"
        f"Graph evidence JSON: {json.dumps(rows, ensure_ascii=False)}"
    )

    try:
        response = httpx.post(
            settings.llm_url,
            json={
                "model": settings.llm_model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1},
            },
            timeout=settings.llm_timeout_seconds,
        )
        response.raise_for_status()
        text = str(response.json().get("response", "")).strip()
        return (text or fallback), ("available" if text else "empty_response")
    except (httpx.HTTPError, ValueError, KeyError):
        return fallback, "unavailable"


def deterministic_answer(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "No matching graph evidence was found."

    first = rows[0]
    if "system_owner_coverage_pct" in first:
        return (
            f"Owning-team coverage for systems is {first['system_owner_coverage_pct']}%; "
            f"business-process owner coverage is {first['process_owner_coverage_pct']}%; "
            f"process-step responsibility coverage is {first['step_responsibility_pct']}%."
        )

    return f"Found {len(rows)} graph evidence row(s). Review the graph and raw evidence below."
