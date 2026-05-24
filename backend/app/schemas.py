from typing import Any

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


class GraphNode(BaseModel):
    name: str
    type: str


class QuestionResponse(BaseModel):
    intent: str
    answer: str
    rows: list[dict[str, Any]]
    graph: dict[str, Any]
    llm_status: str = "not_used"
    query_trace: dict[str, Any] | None = None
