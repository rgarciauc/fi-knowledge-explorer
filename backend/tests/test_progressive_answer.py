from app.evidence_summarizer import summarize_evidence


def test_payment_flow_summary_is_business_meaningful() -> None:
    rows = [
        {
            "source": "End-to-End Payment Execution",
            "source_type": "BusinessProcess",
            "target": "Create payment instruction",
            "target_type": "ProcessStep",
            "relationship": "STEP_1",
        },
        {
            "source": "End-to-End Payment Execution",
            "source_type": "BusinessProcess",
            "target": "Compliance GO or NO-GO decision",
            "target_type": "ProcessStep",
            "relationship": "STEP_3",
        },
        {
            "source": "Sanctions and AML Screening Gate",
            "source_type": "Control",
            "target": "Compliance GO or NO-GO decision",
            "target_type": "ProcessStep",
            "relationship": "APPLIES_TO",
        },
    ]
    result = summarize_evidence("Show payment flow", rows, {"template": "payment_flow"})
    assert "GO or NO-GO" in result
    assert "Found 3 graph evidence" not in result


def test_department_summary_mentions_employee() -> None:
    rows = [
        {
            "source": "IT Compliance Team",
            "source_type": "Team",
            "target": "Amira Haddad",
            "target_type": "Employee",
            "relationship": "HAS_EMPLOYEE",
        }
    ]
    result = summarize_evidence(
        "Who works in compliance?",
        rows,
        {"template": "department_employees", "resolved_term": "compliance"},
    )
    assert "Amira Haddad" in result
    assert "compliance" in result


def test_generic_summary_is_more_useful_than_row_count_only() -> None:
    rows = [
        {
            "source": "A",
            "source_type": "Team",
            "target": "B",
            "target_type": "System",
            "relationship": "MANAGES_SYSTEM",
        }
    ]
    result = summarize_evidence("Show it", rows, {"template": "unknown"})
    assert "MANAGES_SYSTEM" in result
    assert "visible entities" in result
