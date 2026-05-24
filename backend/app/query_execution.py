import logging
from uuid import uuid4

from .config import settings
from .cypher_validator import validate_generated_query
from .db import explain_read_query, read_with_timeout
from .intent_models import GeneratedQueryPlan, ValidationResult


logger = logging.getLogger("super_bank.generated_query")


def execute_generated_read_query(
    plan: GeneratedQueryPlan,
    *,
    request_reference: str | None = None,
) -> tuple[list[dict], ValidationResult]:
    validation = validate_generated_query(plan)
    if not validation.valid:
        logger.warning(
            "generated_query.rejected reasons=%r cypher=%r",
            validation.reasons,
            plan.cypher[:500],
        )
        return [], validation

    metadata = {
        "application": "super_bank",
        "query_method": "validated_generated_read",
        "reference": request_reference or str(uuid4()),
    }
    try:
        explain_read_query(
            plan.cypher,
            validation.safe_parameters,
            timeout_seconds=settings.generated_query_timeout_seconds,
            metadata=metadata,
        )
        rows = read_with_timeout(
            plan.cypher,
            validation.safe_parameters,
            timeout_seconds=settings.generated_query_timeout_seconds,
            metadata=metadata,
        )
        validation.reasons.append("Read-only validation and EXPLAIN planning passed.")
        return rows, validation
    except Exception as exc:
        validation.valid = False
        validation.reasons.append(f"Neo4j rejected or timed out the generated read query: {type(exc).__name__}.")
        return [], validation
