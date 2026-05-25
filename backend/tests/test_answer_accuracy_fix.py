from app.intent_detector import detect_intent

def test_owner_target_extracted_without_entity_catalog_or_ollama() -> None:
    decision, _ = detect_intent(
        "Who are the IT and business owners of Sanctions Monitoring?",
        [],
    )
    assert decision.intent == "system_owners"
    assert decision.term == "Sanctions Monitoring"

def test_failed_system_target_extracted_without_entity_catalog_or_ollama() -> None:
    decision, _ = detect_intent(
        "What is affected if Sanctions Monitoring fails?",
        [],
    )
    assert decision.intent == "system_impact"
    assert decision.term == "Sanctions Monitoring"
