// SUPER_BANK CSV import for Neo4j 2026 / Neo4j 5-compatible Cypher
// This script may be run more than once: nodes and relationships are merged.

// ---------- Constraints ----------
CREATE CONSTRAINT department_id IF NOT EXISTS FOR (n:Department) REQUIRE n.department_id IS UNIQUE;
CREATE CONSTRAINT team_id IF NOT EXISTS FOR (n:Team) REQUIRE n.team_id IS UNIQUE;
CREATE CONSTRAINT employee_id IF NOT EXISTS FOR (n:Employee) REQUIRE n.employee_id IS UNIQUE;
CREATE CONSTRAINT system_id IF NOT EXISTS FOR (n:System) REQUIRE n.system_id IS UNIQUE;
CREATE CONSTRAINT project_id IF NOT EXISTS FOR (n:Project) REQUIRE n.project_id IS UNIQUE;
CREATE CONSTRAINT process_id IF NOT EXISTS FOR (n:BusinessProcess) REQUIRE n.process_id IS UNIQUE;
CREATE CONSTRAINT step_id IF NOT EXISTS FOR (n:ProcessStep) REQUIRE n.step_id IS UNIQUE;
CREATE CONSTRAINT pipeline_id IF NOT EXISTS FOR (n:DataPipeline) REQUIRE n.pipeline_id IS UNIQUE;
CREATE CONSTRAINT dataset_id IF NOT EXISTS FOR (n:Dataset) REQUIRE n.dataset_id IS UNIQUE;

// ---------- Nodes ----------
LOAD CSV WITH HEADERS FROM 'file:///departments.csv' AS row
MERGE (n:Department {department_id: row.department_id})
SET n.name = row.name,
    n.description = row.description,
    n.criticality = row.criticality,
    n.head_employee_id = row.head_employee_id,
    n.status = row.status;

LOAD CSV WITH HEADERS FROM 'file:///teams.csv' AS row
MERGE (n:Team {team_id: row.team_id})
SET n.department_id = row.department_id,
    n.name = row.name,
    n.description = row.description,
    n.team_lead_employee_id = row.team_lead_employee_id,
    n.location = row.location,
    n.criticality = row.criticality;

LOAD CSV WITH HEADERS FROM 'file:///employees.csv' AS row
MERGE (n:Employee {employee_id: row.employee_id})
SET n.department_id = row.department_id,
    n.team_id = row.team_id,
    n.name = row.name,
    n.role = row.role,
    n.manager_employee_id = row.manager_employee_id,
    n.task_summary = row.task_summary,
    n.employment_type = row.employment_type,
    n.location = row.location,
    n.status = row.status;

LOAD CSV WITH HEADERS FROM 'file:///systems_applications.csv' AS row
MERGE (n:System {system_id: row.system_id})
SET n.name = row.name,
    n.type = row.type,
    n.owner_team_id = row.owner_team_id,
    n.description = row.description,
    n.criticality = row.criticality,
    n.data_classification = row.data_classification;

LOAD CSV WITH HEADERS FROM 'file:///projects.csv' AS row
MERGE (n:Project {project_id: row.project_id})
SET n.name = row.name,
    n.sponsoring_department_id = row.sponsoring_department_id,
    n.owning_team_id = row.owning_team_id,
    n.project_manager_employee_id = row.project_manager_employee_id,
    n.description = row.description,
    n.status = row.status,
    n.priority = row.priority,
    n.related_system_ids = row.related_system_ids,
    n.start_date = date(row.start_date),
    n.target_end_date = date(row.target_end_date);

LOAD CSV WITH HEADERS FROM 'file:///business_processes.csv' AS row
MERGE (n:BusinessProcess {process_id: row.process_id})
SET n.name = row.name,
    n.owner_department_id = row.owner_department_id,
    n.owner_team_id = row.owner_team_id,
    n.process_owner_employee_id = row.process_owner_employee_id,
    n.description = row.description,
    n.criticality = row.criticality,
    n.status = row.status;

LOAD CSV WITH HEADERS FROM 'file:///process_steps.csv' AS row
MERGE (n:ProcessStep {step_id: row.step_id})
SET n.process_id = row.process_id,
    n.sequence = toInteger(row.sequence),
    n.name = row.name,
    n.description = row.description,
    n.responsible_team_id = row.responsible_team_id,
    n.responsible_employee_id = row.responsible_employee_id,
    n.expected_output = row.expected_output,
    n.sla_hours = toInteger(row.sla_hours);

LOAD CSV WITH HEADERS FROM 'file:///data_pipelines.csv' AS row
MERGE (n:DataPipeline {pipeline_id: row.pipeline_id})
SET n.name = row.name,
    n.source_system_id = row.source_system_id,
    n.target_dataset_id = row.target_dataset_id,
    n.target_platform_system_id = row.target_platform_system_id,
    n.frequency = row.frequency,
    n.owner_team_id = row.owner_team_id,
    n.status = row.status,
    n.criticality = row.criticality;

LOAD CSV WITH HEADERS FROM 'file:///datasets.csv' AS row
MERGE (n:Dataset {dataset_id: row.dataset_id})
SET n.name = row.name,
    n.classification = row.classification,
    n.source_system_id = row.source_system_id,
    n.description = row.description,
    n.retention_policy = row.retention_policy;

// ---------- Relationships supplied in relationship CSVs ----------
LOAD CSV WITH HEADERS FROM 'file:///department_has_team.csv' AS row
MATCH (d:Department {department_id: row.department_id}), (t:Team {team_id: row.team_id})
MERGE (d)-[:HAS_TEAM]->(t);

LOAD CSV WITH HEADERS FROM 'file:///team_has_employee.csv' AS row
MATCH (t:Team {team_id: row.team_id}), (e:Employee {employee_id: row.employee_id})
MERGE (t)-[:HAS_EMPLOYEE]->(e);

LOAD CSV WITH HEADERS FROM 'file:///employee_reports_to.csv' AS row
MATCH (e:Employee {employee_id: row.employee_id}), (m:Employee {employee_id: row.manager_employee_id})
MERGE (e)-[:REPORTS_TO]->(m);

LOAD CSV WITH HEADERS FROM 'file:///team_owns_system.csv' AS row
MATCH (t:Team {team_id: row.team_id}), (s:System {system_id: row.system_id})
MERGE (t)-[r:OWNS_SYSTEM]->(s)
SET r.ownership_level = row.ownership_level;

LOAD CSV WITH HEADERS FROM 'file:///department_owns_process.csv' AS row
MATCH (d:Department {department_id: row.department_id}), (p:BusinessProcess {process_id: row.process_id})
MERGE (d)-[:OWNS_PROCESS]->(p);

LOAD CSV WITH HEADERS FROM 'file:///process_has_step.csv' AS row
MATCH (p:BusinessProcess {process_id: row.process_id}), (s:ProcessStep {step_id: row.step_id})
MERGE (p)-[r:HAS_STEP]->(s)
SET r.sequence = toInteger(row.sequence);

LOAD CSV WITH HEADERS FROM 'file:///project_uses_system.csv' AS row
MATCH (p:Project {project_id: row.project_id}), (s:System {system_id: row.system_id})
MERGE (p)-[r:USES_SYSTEM]->(s)
SET r.dependency_level = row.dependency_level;

LOAD CSV WITH HEADERS FROM 'file:///team_owns_project.csv' AS row
MATCH (t:Team {team_id: row.team_id}), (p:Project {project_id: row.project_id})
MERGE (t)-[r:OWNS_PROJECT]->(p)
SET r.project_manager_employee_id = row.project_manager_employee_id;

LOAD CSV WITH HEADERS FROM 'file:///process_uses_system.csv' AS row
MATCH (p:BusinessProcess {process_id: row.process_id}), (s:System {system_id: row.system_id})
MERGE (p)-[r:USES_SYSTEM]->(s)
SET r.usage_type = row.usage_type;

LOAD CSV WITH HEADERS FROM 'file:///pipeline_produces_dataset.csv' AS row
MATCH (p:DataPipeline {pipeline_id: row.pipeline_id}), (d:Dataset {dataset_id: row.dataset_id})
MERGE (p)-[:PRODUCES_DATASET]->(d);

LOAD CSV WITH HEADERS FROM 'file:///system_feeds_pipeline.csv' AS row
MATCH (s:System {system_id: row.system_id}), (p:DataPipeline {pipeline_id: row.pipeline_id})
MERGE (s)-[:FEEDS_PIPELINE]->(p);

LOAD CSV WITH HEADERS FROM 'file:///dataset_used_by_process.csv' AS row
MATCH (d:Dataset {dataset_id: row.dataset_id}), (p:BusinessProcess {process_id: row.process_id})
MERGE (d)-[:USED_BY_PROCESS]->(p);

LOAD CSV WITH HEADERS FROM 'file:///project_supports_process.csv' AS row
MATCH (pr:Project {project_id: row.project_id}), (bp:BusinessProcess {process_id: row.process_id})
MERGE (pr)-[:SUPPORTS_PROCESS]->(bp);

// ---------- Additional responsibility links represented in the node CSVs ----------
LOAD CSV WITH HEADERS FROM 'file:///departments.csv' AS row
MATCH (d:Department {department_id: row.department_id}), (e:Employee {employee_id: row.head_employee_id})
MERGE (e)-[:HEADS_DEPARTMENT]->(d);

LOAD CSV WITH HEADERS FROM 'file:///teams.csv' AS row
MATCH (t:Team {team_id: row.team_id}), (e:Employee {employee_id: row.team_lead_employee_id})
MERGE (e)-[:LEADS_TEAM]->(t);

LOAD CSV WITH HEADERS FROM 'file:///business_processes.csv' AS row
MATCH (p:BusinessProcess {process_id: row.process_id}), (e:Employee {employee_id: row.process_owner_employee_id})
MERGE (e)-[:OWNS_PROCESS]->(p);

LOAD CSV WITH HEADERS FROM 'file:///process_steps.csv' AS row
MATCH (s:ProcessStep {step_id: row.step_id}), (e:Employee {employee_id: row.responsible_employee_id})
MERGE (e)-[:RESPONSIBLE_FOR_STEP]->(s);

LOAD CSV WITH HEADERS FROM 'file:///process_steps.csv' AS row
MATCH (s:ProcessStep {step_id: row.step_id}), (t:Team {team_id: row.responsible_team_id})
MERGE (t)-[:PERFORMS_STEP]->(s);

LOAD CSV WITH HEADERS FROM 'file:///data_pipelines.csv' AS row
MATCH (p:DataPipeline {pipeline_id: row.pipeline_id}), (t:Team {team_id: row.owner_team_id})
MERGE (t)-[:OWNS_PIPELINE]->(p);
