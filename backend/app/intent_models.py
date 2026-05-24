from typing import Any, Literal

from pydantic import BaseModel, Field


IntentName = Literal[
    "overview",
    "ownership_search",
    "responsibilities_overview",
    "employee_search",
    "process_pipeline",
    "next_step",
    "system_impact",
    "missing_owners",
    "kpis",
    "global_search",
    "department_employees",
    "generated_read_query",
    "clarification_required",
]


class EntityCandidate(BaseModel):
    label: str
    node_id: str
    name: str
    score: float = Field(ge=0.0, le=1.0)
    description: str = ""


class IntentDecision(BaseModel):
    intent: IntentName
    term: str | None = None
    target_label: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    corrected_question: str | None = None
    reason: str = Field(default="", max_length=600)


class GeneratedQueryPlan(BaseModel):
    cypher: str
    parameters: dict[str, str | int | float | bool] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str = Field(default="", max_length=600)


class ValidationResult(BaseModel):
    valid: bool
    reasons: list[str] = Field(default_factory=list)
    safe_parameters: dict[str, Any] = Field(default_factory=dict)


class QueryTrace(BaseModel):
    query_method: str
    template: str | None = None
    interpreted_intent: str
    confidence: float
    corrected_question: str | None = None
    resolved_term: str | None = None
    entity_candidates: list[EntityCandidate] = Field(default_factory=list)
    fallback_reason: str | None = None
    generated_cypher: str | None = None
    generated_query_validation: list[str] = Field(default_factory=list)
