import json
import logging
from time import perf_counter
from typing import Any

import httpx

from .config import settings


logger = logging.getLogger("super_bank.ollama")


def _ms(nanoseconds: int | float | None) -> int | None:
    return round(nanoseconds / 1_000_000) if nanoseconds is not None else None


def explain(
    question: str,
    rows: list[dict[str, Any]],
    query_trace: dict[str, Any] | None = None,
) -> tuple[str, str]:
    fallback = deterministic_answer(rows)
    if not settings.llm_enabled:
        logger.info("ollama.explanation_skipped reason=disabled")
        return fallback, "disabled"
    if not rows:
        logger.info("ollama.explanation_skipped reason=no_evidence")
        return fallback, "not_called_no_evidence"

    trace = query_trace or {}
    prompt = (
        "You are a SUPER_BANK governance assistant. Answer using only the graph evidence supplied below. "
        "Do not invent ownership, impact or relationships. Mention uncertainty if broad or generated retrieval "
        "does not establish a definitive answer. Use a short clear answer.\n\n"
        f"Question: {question}\n"
        f"Retrieval metadata: {json.dumps(trace, ensure_ascii=False)}\n"
        f"Graph evidence JSON: {json.dumps(rows, ensure_ascii=False)}"
    )

    started = perf_counter()
    logger.info("ollama.explanation_started model=%s evidence_rows=%d", settings.llm_model, len(rows))
    try:
        response = httpx.post(
            settings.llm_url,
            json={
                "model": settings.llm_model,
                "prompt": prompt,
                "stream": False,
                "keep_alive": settings.ollama_keep_alive,
                "options": {"temperature": 0.1},
            },
            timeout=settings.llm_timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        text = str(payload.get("response", "")).strip()
        logger.info(
            "ollama.explanation_completed model=%s wall_ms=%d load_ms=%s prompt_eval_ms=%s eval_ms=%s response_empty=%s",
            settings.llm_model,
            round((perf_counter() - started) * 1000),
            _ms(payload.get("load_duration")),
            _ms(payload.get("prompt_eval_duration")),
            _ms(payload.get("eval_duration")),
            not bool(text),
        )
        return (text or fallback), ("available" if text else "empty_response")
    except (httpx.HTTPError, ValueError, KeyError):
        logger.exception(
            "ollama.explanation_failed model=%s url=%s wall_ms=%d",
            settings.llm_model,
            settings.llm_url,
            round((perf_counter() - started) * 1000),
        )
        return fallback, "unavailable"


def deterministic_answer(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "No matching graph evidence was found. Try naming a system, process, team or dataset."

    first = rows[0]
    if "system_owner_coverage_pct" in first:
        return (
            f"Owning-team coverage for systems is {first['system_owner_coverage_pct']}%; "
            f"business-process owner coverage is {first['process_owner_coverage_pct']}%; "
            f"process-step responsibility coverage is {first['step_responsibility_pct']}%."
        )
    return f"Found {len(rows)} graph evidence row(s). Review the graph and raw evidence below."
