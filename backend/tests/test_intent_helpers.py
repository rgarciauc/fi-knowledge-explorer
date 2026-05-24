from app.service import _failed_system_term, _term_after, classify_question


def test_extract_term_after_for() -> None:
    assert _term_after("Who owns system EMBARGO?", ("system",)) == "EMBARGO"


def test_extract_failed_system_name() -> None:
    assert _failed_system_term("What is affected if system EMBARGO fails?") == "EMBARGO"


def test_impact_intent_uses_starter_system_name() -> None:
    intent, params = classify_question("What is affected if system EMBARGO fails?")
    assert intent == "system_impact"
    assert params["term"] == "EMBARGO"
