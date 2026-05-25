from __future__ import annotations

import json
import logging
from typing import Any, AsyncIterator

from fastapi import Request
from starlette.concurrency import run_in_threadpool

from .config import settings
from .llm import stream_explanation
from .service import answer_question


logger = logging.getLogger("super_bank.streaming")


def _sse(event: str, data: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


async def answer_event_stream(question: str, request: Request) -> AsyncIterator[str]:
    """Return graph evidence immediately, then deliver the AI explanation progressively."""
    result = await run_in_threadpool(answer_question, question)
    original_status = str(result.get("llm_status", "not_used"))
    can_enrich = bool(
        settings.llm_enabled
        and result.get("rows")
        and original_status not in {"not_called_fast_path", "not_called_no_evidence"}
    )
    result["llm_status"] = "generating" if can_enrich else original_status

    yield _sse("evidence_ready", result)

    if not can_enrich:
        yield _sse("answer_complete", {"llm_status": original_status, "answer_ai": ""})
        return

    complete_text = ""
    try:
        async for delta in stream_explanation(
            question,
            result["rows"],
            result.get("query_trace"),
            result.get("answer"),
        ):
            if await request.is_disconnected():
                logger.info("stream.client_disconnected question=%r", question[:120])
                return
            complete_text += delta
            yield _sse("answer_delta", {"delta": delta})

        status = "available" if complete_text.strip() else "empty_response"
        yield _sse("answer_complete", {"llm_status": status, "answer_ai": complete_text.strip()})
    except Exception:
        logger.exception("stream.enrichment_failed question=%r", question[:120])
        yield _sse(
            "answer_error",
            {
                "llm_status": "unavailable",
                "message": "AI explanation is unavailable. The evidence summary and graph remain valid.",
            },
        )
