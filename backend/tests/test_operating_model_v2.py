from app.intent_detector import detect_intent
from app.query_templates import QUERY_TEMPLATES
from app.schema_context import ALLOWED_LABELS, ALLOWED_RELATIONSHIPS

CATALOG = [
    {"label": "System", "node_id": "SYS_SANCTIONS", "name": "Sanctions Monitoring", "description": "Screens payment instructions."},
    {"label": "System", "node_id": "SYS_INPUT", "name": "Input Hub System", "description": "Provides external feeds."},
    {"label": "Employee", "node_id": "E_COMP_IT_LEAD", "name": "Amira Haddad", "description": "Head of IT Compliance."},
    {"label": "Department", "node_id": "D_COMP_IT", "name": "IT Compliance Department", "description": "Technology compliance."},
]

def test_v2_schema_has_new_business_labels_and_relationships() -> None:
    assert {"Control", "Responsibility", "RegulatoryFramework", "ExternalSource"} <= ALLOWED_LABELS
    assert {"IT_OWNER_OF", "BUSINESS_OWNER_OF", "INTERACTS_WITH", "GOVERNS_ACCESS_TO"} <= ALLOWED_RELATIONSHIPS

def test_payment_flow_is_approved_intent(monkeypatch) -> None:
    decision, _ = detect_intent("Show the end-to-end payment flow and GO or NO-GO decision", CATALOG)
    assert decision.intent == "payment_flow"
    assert "payment_flow" in QUERY_TEMPLATES

def test_system_owners_routing(monkeypatch) -> None:
    decision, _ = detect_intent("Who are the IT and business owners of Sanctions Monitoring?", CATALOG)
    assert decision.intent == "system_owners"
    assert decision.term == "Sanctions Monitoring"

def test_data_lineage_routing(monkeypatch) -> None:
    decision, _ = detect_intent("What systems depend on the Input Hub System?", CATALOG)
    assert decision.intent == "data_lineage"
    assert "data_lineage" in QUERY_TEMPLATES
