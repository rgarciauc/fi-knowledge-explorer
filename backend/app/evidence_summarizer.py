from __future__ import annotations

from collections import Counter
from typing import Any


def _unique(rows: list[dict[str, Any]], field: str) -> list[str]:
    values: list[str] = []
    for row in rows:
        value = row.get(field)
        if value and str(value) not in values:
            values.append(str(value))
    return values


def _node_names(rows: list[dict[str, Any]], node_type: str) -> list[str]:
    found: list[str] = []
    for row in rows:
        for side in ("source", "target"):
            if row.get(f"{side}_type") == node_type and row.get(side):
                name = str(row[side])
                if name not in found:
                    found.append(name)
    return found


def _join_names(values: list[str], limit: int = 4) -> str:
    visible = values[:limit]
    if not visible:
        return ""
    if len(visible) == 1:
        text = visible[0]
    elif len(visible) == 2:
        text = f"{visible[0]} and {visible[1]}"
    else:
        text = ", ".join(visible[:-1]) + f", and {visible[-1]}"
    extra = len(values) - len(visible)
    return f"{text} plus {extra} more" if extra > 0 else text


def summarize_evidence(
    question: str,
    rows: list[dict[str, Any]],
    query_trace: dict[str, Any] | None = None,
) -> str:
    """Create an immediate, evidence-only business summary without using the LLM."""
    trace = query_trace or {}
    template = str(trace.get("template") or trace.get("interpreted_intent") or "")
    term = trace.get("resolved_term")
    if not rows:
        return "No matching graph evidence was found. Try naming a team, employee, system, process or dataset."

    first = rows[0]
    if "system_owner_coverage_pct" in first:
        parts = [f"IT/system ownership coverage is {first['system_owner_coverage_pct']}%"]
        if "business_owner_coverage_pct" in first:
            parts.append(f"business ownership coverage is {first['business_owner_coverage_pct']}%")
        elif "process_owner_coverage_pct" in first:
            parts.append(f"business-process ownership coverage is {first['process_owner_coverage_pct']}%")
        if "support_coverage_pct" in first:
            parts.append(f"service-desk support coverage is {first['support_coverage_pct']}%")
        if "access_governance_pct" in first:
            parts.append(f"access-governance coverage is {first['access_governance_pct']}%")
        if "step_responsibility_pct" in first:
            parts.append(f"step assignment coverage is {first['step_responsibility_pct']}%")
        return "; ".join(parts).capitalize() + "."

    relationships = Counter(str(row.get("relationship", "RELATED_TO")) for row in rows)
    systems = _node_names(rows, "System")
    teams = _node_names(rows, "Team")
    employees = _node_names(rows, "Employee")
    processes = _node_names(rows, "BusinessProcess")
    steps = _node_names(rows, "ProcessStep")
    controls = _node_names(rows, "Control")
    frameworks = _node_names(rows, "RegulatoryFramework")
    datasets = _node_names(rows, "Dataset")

    if template == "payment_flow":
        decision = " A GO or NO-GO control is represented before payment release." if controls or any("GO" in name.upper() for name in steps) else ""
        return (
            f"The payment lifecycle shows {len(steps)} visible step(s) across "
            f"{_join_names(teams) or 'the participating teams'}."
            f"{decision} The graph is ready for inspection while a detailed explanation is prepared."
        )

    if template in {"system_owners", "ownership_search"}:
        owners = employees or teams
        target = _join_names(systems) or str(term or "the selected system")
        return (
            f"{target} is connected to {_join_names(owners) or 'its recorded owner(s)'} "
            f"through {len(rows)} ownership or management evidence relationship(s)."
        )

    if template == "department_employees":
        scope = str(term or "the selected department")
        return (
            f"For {scope}, the graph identifies {len(employees)} employee(s)"
            f"{': ' + _join_names(employees, 6) if employees else ''}, connected through "
            f"{_join_names(teams) or 'the matching team structure'}."
        )

    if template == "team_interactions":
        return (
            f"The graph shows {len(rows)} directed operational interaction(s) among "
            f"{len(teams)} team(s), including {_join_names(teams)}."
        )

    if template == "system_impact":
        source = _join_names(systems[:1]) or str(term or "The selected system")
        affected = processes + steps + systems[1:]
        return (
            f"{source} has {len(rows)} visible downstream impact relationship(s)"
            f"{' affecting ' + _join_names(affected, 5) if affected else ''}."
        )

    if template in {"process_pipeline", "next_step"}:
        return (
            f"{_join_names(processes) or 'The selected process'} contains "
            f"{len(steps)} visible process step(s)"
            f"{': ' + _join_names(steps, 6) if steps else ''}."
        )

    if template == "support_coverage":
        return (
            f"Service support evidence connects {_join_names(teams) or 'the participating teams'}"
            f"{' with ' + _join_names(systems) if systems else ''} across {len(rows)} relationship(s)."
        )

    if template == "access_governance":
        return (
            f"Identity and access governance covers {len(systems)} visible system(s)"
            f"{': ' + _join_names(systems, 6) if systems else ''}."
        )

    if template == "regulatory_oversight":
        return (
            f"Regulatory oversight evidence links {_join_names(frameworks) or 'the selected framework'} "
            f"to {len(systems)} visible system(s)"
            f"{': ' + _join_names(systems, 6) if systems else ''}."
        )

    if template == "data_lineage":
        return (
            f"Data-lineage evidence connects {len(systems)} system(s) and {len(datasets)} dataset(s)"
            f"{' including ' + _join_names(systems + datasets, 6) if systems or datasets else ''}."
        )

    top_relationships = ", ".join(
        f"{name} ({count})" for name, count in relationships.most_common(3)
    )
    all_entities = set(_unique(rows, "source") + _unique(rows, "target"))
    return (
        f"The graph retrieved {len(rows)} evidence relationship(s) across {len(all_entities)} visible entities. "
        f"Main relationship types: {top_relationships}. A detailed AI explanation is being prepared."
    )
