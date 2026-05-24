"""Authoritative Bank Operating Model v2 schema context.

This allowlist is aligned with data/bank_operating_model_v2/cypher/import.cypher.
Generated read-only Cypher may use only these labels and relationships.
"""

ALLOWED_LABELS = {
    "Department",
    "Team",
    "Employee",
    "System",
    "ExternalSource",
    "RegulatoryFramework",
    "Control",
    "Responsibility",
    "BusinessProcess",
    "ProcessStep",
    "DataPipeline",
    "Dataset",
    "Project",
}

ALLOWED_RELATIONSHIPS = {
    "HAS_TEAM",
    "HAS_EMPLOYEE",
    "LEADS_TEAM",
    "REPORTS_TO",
    "RESPONSIBLE_FOR",
    "MANAGES_SYSTEM",
    "IT_OWNER_OF",
    "BUSINESS_OWNER_OF",
    "INTERACTS_WITH",
    "SUPPORTS_TEAM",
    "USES_SYSTEM",
    "GOVERNS_ACCESS_TO",
    "DEPENDS_ON",
    "FEEDS_SYSTEM",
    "HAS_STEP",
    "PERFORMS_STEP",
    "APPLIES_TO",
    "IMPLEMENTED_BY",
    "FEEDS_PIPELINE",
    "PRODUCES_DATASET",
    "USED_BY_SYSTEM",
    "USED_BY_PROCESS",
    "MONITORS_FRAMEWORK",
    "DEVELOPS_PROJECT",
}

TERM_INTENTS = {
    "ownership_search",
    "system_owners",
    "employee_search",
    "employee_responsibilities",
    "department_employees",
    "process_pipeline",
    "next_step",
    "system_impact",
    "data_lineage",
    "regulatory_oversight",
    "global_search",
}

TEMPLATE_INTENTS = {
    "overview",
    "ownership_search",
    "system_owners",
    "employee_search",
    "employee_responsibilities",
    "department_employees",
    "payment_flow",
    "team_interactions",
    "process_pipeline",
    "next_step",
    "system_impact",
    "support_coverage",
    "access_governance",
    "regulatory_oversight",
    "data_lineage",
    "missing_owners",
    "kpis",
}

SCHEMA_PROMPT = """
Active SUPER_BANK Bank Operating Model v2 graph schema:
Nodes:
- Department(department_id, name, description, criticality, status)
- Team(team_id, name, description, criticality, location)
- Employee(employee_id, name, role, task_summary, status)
- System(system_id, name, type, description, criticality, data_classification, status)
- ExternalSource(source_id, name, type, description, classification)
- RegulatoryFramework(framework_id, name, type, description)
- Control(control_id, name, type, description, frequency)
- Responsibility(responsibility_id, name, description, category)
- BusinessProcess(process_id, name, description, criticality, status)
- ProcessStep(step_id, name, description, sequence, decision_point)
- DataPipeline(pipeline_id, name, description, criticality, status)
- Dataset(dataset_id, name, description, classification, retention_policy)
- Project(project_id, name, description, status, priority)

Key relationships:
(Department)-[:HAS_TEAM]->(Team)-[:HAS_EMPLOYEE]->(Employee)
(Employee)-[:LEADS_TEAM]->(Team)
(Employee)-[:RESPONSIBLE_FOR]->(Responsibility)
(Team)-[:MANAGES_SYSTEM]->(System)
(Employee)-[:IT_OWNER_OF]->(System)
(Employee)-[:BUSINESS_OWNER_OF]->(System)
(Team)-[:INTERACTS_WITH]->(Team)
(Team)-[:SUPPORTS_TEAM]->(Team)
(Team)-[:USES_SYSTEM]->(System)
(Team)-[:GOVERNS_ACCESS_TO]->(System)
(System)-[:DEPENDS_ON]->(System)
(ExternalSource)-[:FEEDS_SYSTEM]->(System)
(BusinessProcess)-[:HAS_STEP]->(ProcessStep)
(Team)-[:PERFORMS_STEP]->(ProcessStep)
(ProcessStep)-[:USES_SYSTEM]->(System)
(Control)-[:APPLIES_TO]->(ProcessStep)
(Control)-[:IMPLEMENTED_BY]->(System)
(System)-[:FEEDS_PIPELINE]->(DataPipeline)-[:PRODUCES_DATASET]->(Dataset)
(Dataset)-[:USED_BY_SYSTEM]->(System)
(Dataset)-[:USED_BY_PROCESS]->(BusinessProcess)
(Team)-[:MONITORS_FRAMEWORK]->(RegulatoryFramework)-[:APPLIES_TO]->(System)
(Team)-[:DEVELOPS_PROJECT]->(Project)
""".strip()

INTENT_DESCRIPTION = """
Supported execution intents:
- payment_flow: end-to-end payment path including compliance decision, release, settlement and final update.
- team_interactions: interactions/dependencies/collaboration between teams.
- system_owners: IT owner and business owner of a system.
- ownership_search: system management or general ownership.
- department_employees: people working within a named department.
- employee_responsibilities: specific responsibilities assigned to employees.
- employee_search: employee role or task search.
- support_coverage: IT Service Desk support and Ticketing System usage.
- access_governance: Identity Management and system permission governance.
- regulatory_oversight: DORA, GDPR or regulatory-office relationships.
- data_lineage: Input Hub, external feeds, pipelines, datasets and consuming systems.
- system_impact: effects of a system outage or failure.
- process_pipeline: ordered steps of a named process.
- next_step: next step following a named step.
- missing_owners: systems missing IT owner or business owner.
- kpis: governance coverage KPIs.
- overview: high-level banking graph overview.
- global_search: broad neighbourhood search when no approved template fits.
- generated_read_query: complex multi-hop read-only question not covered above.
- clarification_required: the requested meaning remains ambiguous.
""".strip()
