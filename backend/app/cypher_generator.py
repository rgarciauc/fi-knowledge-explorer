import json
import logging

from .intent_models import EntityCandidate, GeneratedQueryPlan
from .ollama_client import structured_generate
from .schema_context import ALLOWED_LABELS, ALLOWED_RELATIONSHIPS, SCHEMA_PROMPT


logger = logging.getLogger("super_bank.generated_query")


def generate_read_query(question: str, candidates: list[EntityCandidate]) -> GeneratedQueryPlan | None:
    prompt = f"""
You generate a single safe READ-ONLY Neo4j Cypher evidence query for a governance graph.
The application will reject any query that modifies data or uses unsupported schema.

{SCHEMA_PROMPT}

Strict requirements:
- Use only MATCH, OPTIONAL MATCH, WHERE, WITH, RETURN, ORDER BY and LIMIT.
- Never use CALL, CREATE, MERGE, SET, DELETE, REMOVE, LOAD CSV, procedures or administration commands.
- Use only allowed labels: {sorted(ALLOWED_LABELS)}.
- Use only allowed relationship types: {sorted(ALLOWED_RELATIONSHIPS)}.
- User/entity values must be parameters, never embedded in the Cypher text.
- Include LIMIT $limit.
- Return graph-display evidence using all exact aliases:
  source_id, source, target_id, target, relationship, source_type, target_type.
- Use stable identifier fields appropriate for each label, for example system_id, process_id,
  team_id, employee_id, department_id, source_id, framework_id, control_id,
  responsibility_id, pipeline_id, dataset_id, step_id or project_id.
- Prefer one or more direct evidence paths instead of an unbounded broad scan.

Question: {question}
Likely matching database entities: {json.dumps([c.model_dump() for c in candidates], ensure_ascii=False)}

Return only JSON matching the required schema with cypher, parameters, confidence and rationale.
""".strip()
    result = structured_generate("generated_read_query", prompt, GeneratedQueryPlan)
    if result:
        logger.info(
            "generated_query.proposed confidence=%.2f rationale=%r",
            result.confidence,
            result.rationale,
        )
    return result
