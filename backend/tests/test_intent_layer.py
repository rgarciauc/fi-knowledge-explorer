from app.config import settings
from app.cypher_validator import validate_generated_query
from app.entity_resolution import find_entity_candidates
from app.intent_detector import detect_intent
from app.intent_models import GeneratedQueryPlan


CATALOG = [
    {
        "label": "System",
        "node_id": "S001",
        "name": "EMBARGO",
        "description": "Sanctions and embargo screening platform.",
    },
    {
        "label": "BusinessProcess",
        "node_id": "BP004",
        "name": "Payment Processing",
        "description": "Process outgoing and incoming payments.",
    },
]


def test_typo_entity_matching_resolves_embargo(monkeypatch) -> None:
    monkeypatch.setattr(settings, "llm_enabled", False)
    monkeypatch.setattr(settings, "intent_detection_enabled", False)
    candidates = find_entity_candidates("What braks if EMABRGO goes down?", CATALOG)
    assert candidates[0].name == "EMBARGO"

    decision, _ = detect_intent("What braks if EMABRGO goes down?", CATALOG)
    assert decision.intent == "system_impact"
    assert decision.term == "EMBARGO"


def test_generated_read_query_accepts_graph_shaped_read_query() -> None:
    plan = GeneratedQueryPlan(
        cypher="""
        MATCH (s:System)-[:FEEDS_PIPELINE]->(p:DataPipeline)
        WHERE toLower(s.name) CONTAINS toLower($term)
        RETURN s.system_id AS source_id, s.name AS source,
               p.pipeline_id AS target_id, p.name AS target,
               'FEEDS_PIPELINE' AS relationship,
               'System' AS source_type, 'DataPipeline' AS target_type
        LIMIT $limit
        """,
        parameters={"term": "EMBARGO"},
        confidence=0.9,
        rationale="Read relationship.",
    )
    result = validate_generated_query(plan)
    assert result.valid is True
    assert result.safe_parameters["limit"] == settings.generated_query_limit


def test_generated_query_rejects_write_operations() -> None:
    plan = GeneratedQueryPlan(
        cypher="""
        MATCH (s:System)
        DELETE s
        RETURN s.system_id AS source_id, s.name AS source,
               s.system_id AS target_id, s.name AS target,
               'SELF' AS relationship, 'System' AS source_type, 'System' AS target_type
        LIMIT $limit
        """,
        parameters={},
        confidence=0.9,
        rationale="Unsafe.",
    )
    result = validate_generated_query(plan)
    assert result.valid is False
    assert any("DELETE" in reason for reason in result.reasons)


def test_generated_query_rejects_procedure_calls() -> None:
    plan = GeneratedQueryPlan(
        cypher="""
        MATCH (s:System)
        CALL db.labels()
        RETURN s.system_id AS source_id, s.name AS source,
               s.system_id AS target_id, s.name AS target,
               'SELF' AS relationship, 'System' AS source_type, 'System' AS target_type
        LIMIT $limit
        """,
        parameters={},
        confidence=0.9,
        rationale="Unsafe.",
    )
    result = validate_generated_query(plan)
    assert result.valid is False
    assert any("CALL" in reason for reason in result.reasons)
