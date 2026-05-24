from fastapi import APIRouter, HTTPException

from .db import node_details, read
from .query_templates import QUERY_TEMPLATES
from .schemas import AskRequest
from .service import answer_question


router = APIRouter(prefix="/api")


@router.post("/ask")
def ask(payload: AskRequest) -> dict:
    return answer_question(payload.question)


@router.get("/nodes/{label}/{node_id}")
def get_node(label: str, node_id: str) -> dict:
    details = node_details(label, node_id)
    if not details:
        raise HTTPException(status_code=404, detail="Node not found")
    return details


@router.get("/kpis")
def get_kpis() -> list[dict]:
    return read(QUERY_TEMPLATES["kpis"])


@router.get("/examples")
def examples() -> list[str]:
    return [
        "Who owns system EMBARGO?",
        "Who is responsible for Sanctions Screening?",
        "What is affected if system EMBARGO fails?",
        "Show the pipeline for Payment Processing",
        "What is the next step after Receive trigger/input - Payment Processing?",
        "Show missing system owners",
        "Show KPI summary",
    ]
