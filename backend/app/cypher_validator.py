import re

from .config import settings
from .intent_models import GeneratedQueryPlan, ValidationResult
from .schema_context import ALLOWED_LABELS, ALLOWED_RELATIONSHIPS


FORBIDDEN_TOKENS = {
    "CREATE", "MERGE", "SET", "DELETE", "DETACH", "REMOVE", "DROP", "ALTER",
    "RENAME", "LOAD", "CSV", "FOREACH", "CALL", "YIELD", "SHOW", "TERMINATE",
    "GRANT", "DENY", "REVOKE", "START", "STOP", "APOC", "DBMS", "PROFILE",
    "EXPLAIN", "USE",
}

REQUIRED_OUTPUT_ALIASES = {
    "source_id",
    "source",
    "target_id",
    "target",
    "relationship",
    "source_type",
    "target_type",
}


def _without_literals_and_comments(query: str) -> str:
    text = re.sub(r"//.*?$", " ", query, flags=re.MULTILINE)
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.DOTALL)
    text = re.sub(r"'(?:''|[^'])*'", "''", text)
    text = re.sub(r'"(?:""|[^"])*"', '""', text)
    return text


def validate_generated_query(plan: GeneratedQueryPlan) -> ValidationResult:
    query = plan.cypher.strip()
    reasons: list[str] = []
    inspectable = _without_literals_and_comments(query)
    uppercase = inspectable.upper()

    if not query:
        reasons.append("Generated Cypher is empty.")
    if ";" in inspectable:
        reasons.append("Multiple statements or semicolons are not allowed.")
    if not re.match(r"^\s*(MATCH|OPTIONAL\s+MATCH)\b", uppercase):
        reasons.append("Generated Cypher must start with MATCH or OPTIONAL MATCH.")
    if not re.search(r"\bRETURN\b", uppercase):
        reasons.append("Generated Cypher must contain RETURN.")
    if not re.search(r"\bLIMIT\s+\$limit\b", inspectable, flags=re.IGNORECASE):
        reasons.append("Generated Cypher must enforce LIMIT $limit.")

    found_forbidden = sorted(
        token for token in FORBIDDEN_TOKENS
        if re.search(rf"\b{re.escape(token)}\b", uppercase)
    )
    if found_forbidden:
        reasons.append(f"Forbidden Cypher token(s): {', '.join(found_forbidden)}.")

    if re.search(r"\[[^\]]*\*", inspectable):
        reasons.append("Variable-length relationship patterns are not allowed in generated queries.")

    labels = set(re.findall(r"\([^)]*:\s*([A-Za-z][A-Za-z0-9_]*)", inspectable))
    unknown_labels = sorted(labels - ALLOWED_LABELS)
    if unknown_labels:
        reasons.append(f"Unknown node label(s): {', '.join(unknown_labels)}.")

    relationships = set(re.findall(r"\[[^\]]*:\s*([A-Za-z][A-Za-z0-9_]*)", inspectable))
    unknown_relationships = sorted(relationships - ALLOWED_RELATIONSHIPS)
    if unknown_relationships:
        reasons.append(f"Unknown relationship type(s): {', '.join(unknown_relationships)}.")

    aliases = set(re.findall(r"\bAS\s+([A-Za-z][A-Za-z0-9_]*)", inspectable, flags=re.IGNORECASE))
    missing_aliases = sorted(REQUIRED_OUTPUT_ALIASES - {alias.lower() for alias in aliases})
    if missing_aliases:
        reasons.append(
            "Generated graph query must return aliased graph evidence columns: "
            + ", ".join(missing_aliases)
            + "."
        )

    parameter_names = set(re.findall(r"\$([A-Za-z][A-Za-z0-9_]*)", inspectable))
    missing_parameters = sorted(parameter_names - set(plan.parameters) - {"limit"})
    if missing_parameters:
        reasons.append(f"Missing generated parameter value(s): {', '.join(missing_parameters)}.")

    safe_parameters = dict(plan.parameters)
    safe_parameters["limit"] = settings.generated_query_limit
    return ValidationResult(valid=not reasons, reasons=reasons, safe_parameters=safe_parameters)
