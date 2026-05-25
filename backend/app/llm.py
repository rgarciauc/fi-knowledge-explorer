from __future__ import annotations

import json
import logging
from time import perf_counter
from typing import Any, AsyncIterator

import httpx

from .config import settings
from .evidence_summarizer import summarize_evidence


logger = logging.getLogger("super_bank.ollama")


def _ms(nanoseconds: int | float | None) -> int | None:
    return round(nanoseconds / 1_000_000) if nanoseconds is not None else None


def _prompt(question: str, rows: list[dict[str, Any]], query_trace: dict[str, Any], fast_answer: str) -> str:
    return (
        "You are the AI explanation layer for a bank knowledge-graph application. "
        "The user already sees an immediate deterministic graph summary and an interactive graph. "
        "Write a concise, high-value explanation grounded ONLY in the supplied graph evidence. "
        "Do not invent people, owners, systems, controls, decisions, regulations or impact paths. "
        "Distinguish recorded evidence from inference. Explain business relevance in plain language. "
        "Avoid saying 'rows' or repeating the immediate summary verbatim. Use 2 to 4 short paragraphs "
        "or a compact bullet list when a sequence is present.\n\n"
        f"Question: {question}\n"
        f"Immediate evidence summary: {fast_answer}\n"
        f"Retrieval metadata: {json.dumps(query_trace, ensure_ascii=False)}\n"
        f"Graph evidence JSON: {json.dumps(rows, ensure_ascii=False)}"
    )


def explain(
    question: str,
    rows: list[dict[str, Any]],
    query_trace: dict[str, Any] | None = None,
) -> tuple[str, str]:
    """Return a fast evidence-backed summary; streaming enrichment is a separate endpoint."""
    trace = query_trace or {}
    summary = summarize_evidence(question, rows, trace)
    if not rows:
        return summary, "not_called_no_evidence"
    if not settings.llm_enabled:
        logger.info("ollama.explanation_skipped reason=disabled mode=progressive")
        return summary, "disabled"
    return summary, "evidence_only"


async def stream_explanation(
    question: str,
    rows: list[dict[str, Any]],
    query_trace: dict[str, Any] | None = None,
    fast_answer: str | None = None,
) -> AsyncIterator[str]:
    """Stream only the richer AI narrative after evidence is already displayed."""
    if not settings.llm_enabled or not rows:
        return

    trace = query_trace or {}
    summary = fast_answer or summarize_evidence(question, rows, trace)
    prompt = _prompt(question, rows, trace, summary)
    started = perf_counter()
    emitted = False
    final_payload: dict[str, Any] = {}

    logger.info("ollama.progressive_started model=%s evidence_rows=%d", settings.llm_model, len(rows))
    try:
        async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds, trust_env=False) as client:
            async with client.stream(
                "POST",
                settings.llm_url,
                json={
                    "model": settings.llm_model,
                    "prompt": prompt,
                    "stream": True,
                    "keep_alive": settings.ollama_keep_alive,
                    "options": {"temperature": 0.1},
                },
            ) as response:
                if not response.is_success:
                    body = (await response.aread()).decode("utf-8", errors="replace")[:800]
                    logger.error(
                        "ollama.progressive_http_error model=%s status=%d body=%r url=%s",
                        settings.llm_model,
                        response.status_code,
                        body,
                        settings.llm_url,
                    )
                    response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    payload = json.loads(line)
                    if payload.get("error"):
                        raise RuntimeError(f"Ollama stream error: {payload['error']}")
                    final_payload = payload
                    delta = str(payload.get("response", ""))
                    if delta:
                        emitted = True
                        yield delta
                    if payload.get("done") is True:
                        break
        logger.info(
            "ollama.progressive_completed model=%s wall_ms=%d load_ms=%s prompt_eval_ms=%s eval_ms=%s emitted=%s",
            settings.llm_model,
            round((perf_counter() - started) * 1000),
            _ms(final_payload.get("load_duration")),
            _ms(final_payload.get("prompt_eval_duration")),
            _ms(final_payload.get("eval_duration")),
            emitted,
        )
    except (httpx.HTTPError, ValueError, KeyError, json.JSONDecodeError, RuntimeError):
        logger.exception(
            "ollama.progressive_failed model=%s url=%s wall_ms=%d",
            settings.llm_model,
            settings.llm_url,
            round((perf_counter() - started) * 1000),
        )
        raise
