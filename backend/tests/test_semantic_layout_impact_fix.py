from app.evidence_summarizer import summarize_evidence
from app.intent_detector import detect_intent

CATALOG = [
    {
        "label": "System",
        "node_id": "SYS_SANCTIONS",
        "name": "Sanctions Monitoring",
        "description": "Screens payment instructions.",
    },
    {
        "label": "System",
        "node_id": "SYS_MARKET",
        "name": "Compliance Market Abuse Surveillance",
        "description": "Market abuse alert monitoring.",
    },
    {
        "label": "Control",
        "node_id": "CTRL_MARKET",
        "name": "Market Abuse Alert Monitoring",
        "description": "Detects alerts.",
    },
]


def test_failure_question_prefers_explicit_failed_system() -> None:
    decision, _ = detect_intent("What is affected if Sanctions Monitoring fails?", CATALOG)
    assert decision.intent == "system_impact"
    assert decision.term == "Sanctions Monitoring"
    assert decision.confidence >= 0.99


def test_system_impact_summary_mentions_payment_dependency() -> None:
    rows = [
        {
            "source": "Sanctions Monitoring",
            "source_type": "System",
            "target": "Payment Processing Core",
            "target_type": "System",
            "relationship": "IMPACTS_DEPENDENT_SYSTEM",
        },
        {
            "source": "Sanctions Monitoring",
            "source_type": "System",
            "target": "End-to-End Payment Execution",
            "target_type": "BusinessProcess",
            "relationship": "IMPACTS_BUSINESS_PROCESS",
        },
        {
            "source": "Sanctions Monitoring",
            "source_type": "System",
            "target": "Sanctions and AML Screening Gate",
            "target_type": "Control",
            "relationship": "IMPLEMENTS_CONTROL",
        },
    ]
    summary = summarize_evidence(
        "What is affected if Sanctions Monitoring fails?",
        rows,
        {"template": "system_impact", "resolved_term": "Sanctions Monitoring"},
    )
    assert "Payment Processing Core" in summary
    assert "End-to-End Payment Execution" in summary
    assert "Sanctions and AML Screening Gate" in summary
