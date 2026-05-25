import logging

from fastapi import Request
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, HTTPException
from .db import node_details, read
from .query_templates import QUERY_TEMPLATES
from .schemas import AskRequest
from .service import answer_question
from .streaming_answer import answer_event_stream

logger = logging.getLogger("super_bank.api")
router = APIRouter(prefix="/api")

@router.post("/ask")
def ask(payload: AskRequest) -> dict:
    return answer_question(payload.question)

@router.post("/ask/stream")
async def ask_stream(payload: AskRequest, request: Request) -> StreamingResponse:
    # Progressive answer: evidence first, then streamed grounded AI explanation.
    return StreamingResponse(
        answer_event_stream(payload.question, request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/nodes/{label}/{node_id}")
def get_node(label: str, node_id: str) -> dict:
    try:
        details = node_details(label, node_id)
    except Exception as exc:
        logger.exception("node_detail_endpoint_failed label=%s node_id=%s", label, node_id)
        raise HTTPException(status_code=500, detail=f"Node details could not be loaded for {label}/{node_id}.") from exc
    if not details:
        raise HTTPException(status_code=404, detail="Node not found")
    return details

@router.get("/kpis")
def get_kpis() -> list[dict]:
    return read(QUERY_TEMPLATES["kpis"])

@router.get("/examples")
def examples() -> list[str]:
    return [
        "Show the end-to-end payment flow and GO or NO-GO decision",
        "How do the IT Payments and IT Compliance teams interact?",
        "Who are the IT and business owners of Sanctions Monitoring?",
        "Who works in the IT Compliance Department?",
        "What systems depend on the Input Hub System?",
        "How does the IT Service Desk support all teams?",
        "Which systems are governed by Identity Management?",
        "Which systems are under DORA oversight?",
        "What responsibilities does Amira Haddad have?",
        "What is affected if Sanctions Monitoring fails?",
    ]
