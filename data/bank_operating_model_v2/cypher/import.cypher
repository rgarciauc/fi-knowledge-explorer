// SUPER_BANK Bank Operating Model v2
// Versioned replacement dataset import for Neo4j 2026 / Neo4j 5-compatible Cypher.
// Re-runnable for additions and property updates. For clean model activation, use the supplied activation script.

// ---------------- Constraints ----------------
CREATE CONSTRAINT department_id IF NOT EXISTS FOR (n:Department) REQUIRE n.department_id IS UNIQUE;
CREATE CONSTRAINT team_id IF NOT EXISTS FOR (n:Team) REQUIRE n.team_id IS UNIQUE;
CREATE CONSTRAINT employee_id IF NOT EXISTS FOR (n:Employee) REQUIRE n.employee_id IS UNIQUE;
CREATE CONSTRAINT system_id IF NOT EXISTS FOR (n:System) REQUIRE n.system_id IS UNIQUE;
CREATE CONSTRAINT external_source_id IF NOT EXISTS FOR (n:ExternalSource) REQUIRE n.source_id IS UNIQUE;
CREATE CONSTRAINT framework_id IF NOT EXISTS FOR (n:RegulatoryFramework) REQUIRE n.framework_id IS UNIQUE;
CREATE CONSTRAINT control_id IF NOT EXISTS FOR (n:Control) REQUIRE n.control_id IS UNIQUE;
CREATE CONSTRAINT responsibility_id IF NOT EXISTS FOR (n:Responsibility) REQUIRE n.responsibility_id IS UNIQUE;
CREATE CONSTRAINT process_id IF NOT EXISTS FOR (n:BusinessProcess) REQUIRE n.process_id IS UNIQUE;
CREATE CONSTRAINT step_id IF NOT EXISTS FOR (n:ProcessStep) REQUIRE n.step_id IS UNIQUE;
CREATE CONSTRAINT pipeline_id IF NOT EXISTS FOR (n:DataPipeline) REQUIRE n.pipeline_id IS UNIQUE;
CREATE CONSTRAINT dataset_id IF NOT EXISTS FOR (n:Dataset) REQUIRE n.dataset_id IS UNIQUE;
CREATE CONSTRAINT project_id IF NOT EXISTS FOR (n:Project) REQUIRE n.project_id IS UNIQUE;

// ---------------- Nodes ----------------
LOAD CSV WITH HEADERS FROM 'file:///departments.csv' AS row
MERGE (n:Department {department_id: row.department_id})
SET n.name=row.name, n.description=row.description, n.criticality=row.criticality, n.status=row.status, n.model_version='v2';

LOAD CSV WITH HEADERS FROM 'file:///teams.csv' AS row
MERGE (n:Team {team_id: row.team_id})
SET n.department_id=row.department_id, n.name=row.name, n.description=row.description,
    n.lead_employee_id=row.lead_employee_id, n.location=row.location, n.criticality=row.criticality, n.model_version='v2';

LOAD CSV WITH HEADERS FROM 'file:///employees.csv' AS row
MERGE (n:Employee {employee_id: row.employee_id})
SET n.team_id=row.team_id, n.name=row.name, n.role=row.role, n.task_summary=row.task_summary, n.status=row.status, n.model_version='v2';

LOAD CSV WITH HEADERS FROM 'file:///systems.csv' AS row
MERGE (n:System {system_id: row.system_id})
SET n.name=row.name, n.type=row.system_type, n.description=row.description, n.criticality=row.criticality,
    n.data_classification=row.data_classification, n.status=row.status, n.model_version='v2';

LOAD CSV WITH HEADERS FROM 'file:///external_sources.csv' AS row
MERGE (n:ExternalSource {source_id: row.source_id})
SET n.name=row.name, n.type=row.source_type, n.description=row.description, n.classification=row.classification, n.model_version='v2';

LOAD CSV WITH HEADERS FROM 'file:///frameworks.csv' AS row
MERGE (n:RegulatoryFramework {framework_id: row.framework_id})
SET n.name=row.name, n.type=row.framework_type, n.description=row.description, n.model_version='v2';

LOAD CSV WITH HEADERS FROM 'file:///controls.csv' AS row
MERGE (n:Control {control_id: row.control_id})
SET n.name=row.name, n.type=row.control_type, n.description=row.description, n.frequency=row.frequency, n.model_version='v2';

LOAD CSV WITH HEADERS FROM 'file:///responsibilities.csv' AS row
MERGE (n:Responsibility {responsibility_id: row.responsibility_id})
SET n.name=row.name, n.description=row.description, n.category=row.category, n.model_version='v2';

LOAD CSV WITH HEADERS FROM 'file:///business_processes.csv' AS row
MERGE (n:BusinessProcess {process_id: row.process_id})
SET n.name=row.name, n.description=row.description, n.criticality=row.criticality, n.status=row.status, n.model_version='v2';

LOAD CSV WITH HEADERS FROM 'file:///process_steps.csv' AS row
MERGE (n:ProcessStep {step_id: row.step_id})
SET n.process_id=row.process_id, n.sequence=toInteger(row.sequence), n.name=row.name, n.description=row.description,
    n.decision_point=row.decision_point, n.model_version='v2';

LOAD CSV WITH HEADERS FROM 'file:///pipelines.csv' AS row
MERGE (n:DataPipeline {pipeline_id: row.pipeline_id})
SET n.name=row.name, n.description=row.description, n.criticality=row.criticality, n.status=row.status, n.model_version='v2';

LOAD CSV WITH HEADERS FROM 'file:///datasets.csv' AS row
MERGE (n:Dataset {dataset_id: row.dataset_id})
SET n.name=row.name, n.description=row.description, n.classification=row.classification,
    n.retention_policy=row.retention_policy, n.model_version='v2';

LOAD CSV WITH HEADERS FROM 'file:///projects.csv' AS row
MERGE (n:Project {project_id: row.project_id})
SET n.name=row.name, n.description=row.description, n.status=row.status, n.priority=row.priority, n.model_version='v2';

// ---------------- Organisation and accountability ----------------
LOAD CSV WITH HEADERS FROM 'file:///department_has_team.csv' AS row
MATCH (d:Department {department_id: row.department_id}), (t:Team {team_id: row.team_id})
MERGE (d)-[:HAS_TEAM]->(t);

LOAD CSV WITH HEADERS FROM 'file:///team_has_employee.csv' AS row
MATCH (t:Team {team_id: row.team_id}), (e:Employee {employee_id: row.employee_id})
MERGE (t)-[:HAS_EMPLOYEE]->(e);

LOAD CSV WITH HEADERS FROM 'file:///team_leads.csv' AS row
MATCH (e:Employee {employee_id: row.employee_id}), (t:Team {team_id: row.team_id})
MERGE (e)-[:LEADS_TEAM]->(t);

LOAD CSV WITH HEADERS FROM 'file:///employee_reports_to.csv' AS row
MATCH (e:Employee {employee_id: row.employee_id}), (m:Employee {employee_id: row.manager_employee_id})
MERGE (e)-[:REPORTS_TO]->(m);

LOAD CSV WITH HEADERS FROM 'file:///employee_has_responsibility.csv' AS row
MATCH (e:Employee {employee_id: row.employee_id}), (r:Responsibility {responsibility_id: row.responsibility_id})
MERGE (e)-[:RESPONSIBLE_FOR]->(r);

// ---------------- Systems, owners and team interactions ----------------
LOAD CSV WITH HEADERS FROM 'file:///team_manages_system.csv' AS row
MATCH (t:Team {team_id: row.team_id}), (s:System {system_id: row.system_id})
MERGE (t)-[rel:MANAGES_SYSTEM]->(s)
SET rel.management_role=row.management_role;

LOAD CSV WITH HEADERS FROM 'file:///employee_it_owns_system.csv' AS row
MATCH (e:Employee {employee_id: row.employee_id}), (s:System {system_id: row.system_id})
MERGE (e)-[:IT_OWNER_OF]->(s);

LOAD CSV WITH HEADERS FROM 'file:///employee_business_owns_system.csv' AS row
MATCH (e:Employee {employee_id: row.employee_id}), (s:System {system_id: row.system_id})
MERGE (e)-[:BUSINESS_OWNER_OF]->(s);

LOAD CSV WITH HEADERS FROM 'file:///team_interactions.csv' AS row
MATCH (a:Team {team_id: row.source_team_id}), (b:Team {team_id: row.target_team_id})
MERGE (a)-[rel:INTERACTS_WITH {interaction_type: row.interaction_type}]->(b)
SET rel.description=row.description;

LOAD CSV WITH HEADERS FROM 'file:///service_desk_supports_team.csv' AS row
MATCH (service:Team {team_id: row.support_team_id}), (supported:Team {team_id: row.supported_team_id})
MERGE (service)-[rel:SUPPORTS_TEAM]->(supported)
SET rel.support_level=row.support_level;

LOAD CSV WITH HEADERS FROM 'file:///team_uses_system.csv' AS row
MATCH (t:Team {team_id: row.team_id}), (s:System {system_id: row.system_id})
MERGE (t)-[rel:USES_SYSTEM]->(s)
SET rel.usage_purpose=row.usage_purpose;

LOAD CSV WITH HEADERS FROM 'file:///iam_governs_system.csv' AS row
MATCH (iam:Team {team_id: row.team_id}), (s:System {system_id: row.system_id})
MERGE (iam)-[:GOVERNS_ACCESS_TO]->(s);

LOAD CSV WITH HEADERS FROM 'file:///system_dependencies.csv' AS row
MATCH (dependent:System {system_id: row.dependent_system_id}), (provider:System {system_id: row.provider_system_id})
MERGE (dependent)-[rel:DEPENDS_ON]->(provider)
SET rel.dependency_type=row.dependency_type, rel.description=row.description;

LOAD CSV WITH HEADERS FROM 'file:///external_source_feeds_system.csv' AS row
MATCH (source:ExternalSource {source_id: row.source_id}), (system:System {system_id: row.system_id})
MERGE (source)-[rel:FEEDS_SYSTEM]->(system)
SET rel.description=row.description;

// ---------------- Operational process flows ----------------
LOAD CSV WITH HEADERS FROM 'file:///process_has_step.csv' AS row
MATCH (p:BusinessProcess {process_id: row.process_id}), (step:ProcessStep {step_id: row.step_id})
MERGE (p)-[rel:HAS_STEP]->(step)
SET rel.sequence=toInteger(row.sequence);

LOAD CSV WITH HEADERS FROM 'file:///team_performs_step.csv' AS row
MATCH (t:Team {team_id: row.team_id}), (step:ProcessStep {step_id: row.step_id})
MERGE (t)-[:PERFORMS_STEP]->(step);

LOAD CSV WITH HEADERS FROM 'file:///step_uses_system.csv' AS row
MATCH (step:ProcessStep {step_id: row.step_id}), (system:System {system_id: row.system_id})
MERGE (step)-[:USES_SYSTEM]->(system);

LOAD CSV WITH HEADERS FROM 'file:///process_uses_system.csv' AS row
MATCH (p:BusinessProcess {process_id: row.process_id}), (system:System {system_id: row.system_id})
MERGE (p)-[:USES_SYSTEM]->(system);

LOAD CSV WITH HEADERS FROM 'file:///control_applies_to_step.csv' AS row
MATCH (control:Control {control_id: row.control_id}), (step:ProcessStep {step_id: row.step_id})
MERGE (control)-[:APPLIES_TO]->(step);

LOAD CSV WITH HEADERS FROM 'file:///control_implemented_by_system.csv' AS row
MATCH (control:Control {control_id: row.control_id}), (system:System {system_id: row.system_id})
MERGE (control)-[:IMPLEMENTED_BY]->(system);

// ---------------- Data lineage ----------------
LOAD CSV WITH HEADERS FROM 'file:///system_feeds_pipeline.csv' AS row
MATCH (system:System {system_id: row.system_id}), (pipeline:DataPipeline {pipeline_id: row.pipeline_id})
MERGE (system)-[:FEEDS_PIPELINE]->(pipeline);

LOAD CSV WITH HEADERS FROM 'file:///pipeline_produces_dataset.csv' AS row
MATCH (pipeline:DataPipeline {pipeline_id: row.pipeline_id}), (dataset:Dataset {dataset_id: row.dataset_id})
MERGE (pipeline)-[:PRODUCES_DATASET]->(dataset);

LOAD CSV WITH HEADERS FROM 'file:///dataset_used_by_system.csv' AS row
MATCH (dataset:Dataset {dataset_id: row.dataset_id}), (system:System {system_id: row.system_id})
MERGE (dataset)-[:USED_BY_SYSTEM]->(system);

LOAD CSV WITH HEADERS FROM 'file:///dataset_used_by_process.csv' AS row
MATCH (dataset:Dataset {dataset_id: row.dataset_id}), (process:BusinessProcess {process_id: row.process_id})
MERGE (dataset)-[:USED_BY_PROCESS]->(process);

// ---------------- Regulatory oversight and innovation ----------------
LOAD CSV WITH HEADERS FROM 'file:///framework_applies_to_system.csv' AS row
MATCH (framework:RegulatoryFramework {framework_id: row.framework_id}), (system:System {system_id: row.system_id})
MERGE (framework)-[:APPLIES_TO]->(system);

LOAD CSV WITH HEADERS FROM 'file:///regulatory_team_monitors_framework.csv' AS row
MATCH (team:Team {team_id: row.team_id}), (framework:RegulatoryFramework {framework_id: row.framework_id})
MERGE (team)-[:MONITORS_FRAMEWORK]->(framework);

LOAD CSV WITH HEADERS FROM 'file:///team_develops_project.csv' AS row
MATCH (team:Team {team_id: row.team_id}), (project:Project {project_id: row.project_id})
MERGE (team)-[:DEVELOPS_PROJECT]->(project);

// ---------------- Import verification output ----------------
MATCH (n)
WHERE n.model_version = 'v2'
RETURN labels(n)[0] AS imported_label, count(*) AS imported_nodes
ORDER BY imported_label;
