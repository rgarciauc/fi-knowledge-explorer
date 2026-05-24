# Schema, query catalogue and KPI extensions

## Core modelling rules

- Every entity has a stable identifier independent of its display name.
- Ownership is a relationship, not a property; it can later carry validity dates and delegation status.
- Process steps are first-class nodes because they need owners, SLAs, systems and controls.
- A system dependency direction answers impact: `(consumer)-[:DEPENDS_ON]->(required_system)`.
- Controls mitigate risks and attach to process steps where they operate.

## Starter KPIs computed from the graph

| KPI | Definition | Value from seed data |
| --- | --- | --- |
| System ownership coverage | Systems with IT and business owner / systems | Expected 100% |
| Process accountability coverage | Processes with an accountable owning department / processes | Expected 100% |
| Step accountability coverage | Steps with accountable employee / steps | Expected 100% |
| Control coverage | Critical processes having at least one control / critical processes | Query-ready |
| System blast radius | Count of processes using a system or dependent systems | Query-ready per system |
| Concentration risk | Critical systems owned by the same employee | Query-ready |

## Important later datasets

Add `incidents.csv`, `control_tests.csv`, `sla_executions.csv`, `audit_findings.csv`, `vendors.csv`, `data_assets.csv`, and relationship files. Without event/history data the graph can show structural exposure, but it cannot honestly report operational performance such as mean-time-to-recover or SLA breach rate.
