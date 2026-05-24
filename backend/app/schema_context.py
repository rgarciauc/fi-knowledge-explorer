"""Authoritative schema context for intent recognition and safe query generation.

These labels and relationships match data/neo4j_starter/cypher/import.cypher.
Generated Cypher is restricted to this allowlist.
"""

ALLOWED_LABELS = {
    "Department",
    "Team",
    "Employee",
    "System",
    "Project",
    "BusinessProcess",
    "ProcessStep",
    "DataPipeline",
    "Dataset",
}

ALLOWED_RELATIONSHIPS = {
    "HAS_TEAM",
    "HAS_EMPLOYEE",
    "REPORTS_TO",
    "OWNS_SYSTEM",
    "OWNS_PROCESS",
    "HAS_STEP",
    "USES_SYSTEM",
    "OWNS_PROJECT",
    "PRODUCES_DATASET",
    "FEEDS_PIPELINE",
    "USED_BY_PROCESS",
    "SUPPORTS_PROCESS",
    "HEADS_DEPARTMENT",
    "LEADS_TEAM",
    "RESPONSIBLE_FOR_STEP",
    "PERFORMS_STEP",
    "OWNS_PIPELINE",
}

TERM_INTENTS = {
    "ownership_search",
    "employee_search",
    "process_pipeline",
    "next_step",
    "system_impact",
    "global_search",
    "department_employees",
}

TEMPLATE_INTENTS = {
    "overview",
    "ownership_search",
    "responsibilities_overview",
    "employee_search",
    "process_pipeline",
    "next_step",
    "system_impact",
    "missing_owners",
    "kpis",
    "department_employees",
}

SCHEMA_PROMPT = """
Active SUPER_BANK graph schema:
Nodes:
- Department(department_id, name, description, criticality, status)
- Team(team_id, name, description, criticality, location)
- Employee(employee_id, name, role, task_summary, status)
- System(system_id, name, type, description, criticality, data_classification)
- Project(project_id, name, description, status, priority)
- BusinessProcess(process_id, name, description, criticality, status)
- ProcessStep(step_id, name, description, sequence, expected_output, sla_hours)
- DataPipeline(pipeline_id, name, frequency, status, criticality)
- Dataset(dataset_id, name, description, classification, retention_policy)

Relationships:
(Department)-[:HAS_TEAM]->(Team)
(Team)-[:HAS_EMPLOYEE]->(Employee)
(Employee)-[:REPORTS_TO]->(Employee)
(Team)-[:OWNS_SYSTEM]->(System)
(Department)-[:OWNS_PROCESS]->(BusinessProcess)
(Employee)-[:OWNS_PROCESS]->(BusinessProcess)
(BusinessProcess)-[:HAS_STEP]->(ProcessStep)
(Employee)-[:RESPONSIBLE_FOR_STEP]->(ProcessStep)
(Team)-[:PERFORMS_STEP]->(ProcessStep)
(BusinessProcess)-[:USES_SYSTEM]->(System)
(Project)-[:USES_SYSTEM]->(System)
(Team)-[:OWNS_PROJECT]->(Project)
(System)-[:FEEDS_PIPELINE]->(DataPipeline)
(DataPipeline)-[:PRODUCES_DATASET]->(Dataset)
(Dataset)-[:USED_BY_PROCESS]->(BusinessProcess)
(Project)-[:SUPPORTS_PROCESS]->(BusinessProcess)
(Team)-[:OWNS_PIPELINE]->(DataPipeline)
""".strip()

INTENT_DESCRIPTION = """
Supported execution intents:
- ownership_search: owner of a system or business process.
- system_impact: consequences, dependencies or downstream impact of a failed/unavailable system.
- process_pipeline: ordered steps of a business process.
- next_step: next step after a specific process step.
- employee_search: employee role, task or responsibility search.
- missing_owners: systems without an owning team.
- kpis: coverage or governance KPI summary.
- responsibilities_overview: overview of responsibility/ownership links.
- overview: general organization overview.
- department_employees: employees and teams working in a department.\n- global_search: broad exploration around an entity or topic, such as everything related to payments.
- generated_read_query: a complex multi-hop question not answered by approved templates.
- clarification_required: ambiguity remains after considering the supplied candidate entities.
""".strip()
