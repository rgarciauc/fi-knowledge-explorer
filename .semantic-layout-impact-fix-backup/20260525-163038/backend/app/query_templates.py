"""Read-only Bank Operating Model v2 Cypher templates.

Aligned with data/bank_operating_model_v2/cypher/import.cypher.
All graph-producing templates return:
source_id, source, target_id, target, relationship, source_type, target_type.
"""

QUERY_TEMPLATES = {
    "overview": """
        CALL {
            MATCH (d:Department)-[:HAS_TEAM]->(t:Team)
            RETURN d.department_id AS source_id, d.name AS source,
                   t.team_id AS target_id, t.name AS target,
                   'HAS_TEAM' AS relationship, 'Department' AS source_type, 'Team' AS target_type
            UNION ALL
            MATCH (a:Team)-[r:INTERACTS_WITH]->(b:Team)
            RETURN a.team_id AS source_id, a.name AS source,
                   b.team_id AS target_id, b.name AS target,
                   coalesce(r.interaction_type, 'INTERACTS_WITH') AS relationship,
                   'Team' AS source_type, 'Team' AS target_type
            UNION ALL
            MATCH (t:Team)-[:MANAGES_SYSTEM]->(s:System)
            RETURN t.team_id AS source_id, t.name AS source,
                   s.system_id AS target_id, s.name AS target,
                   'MANAGES_SYSTEM' AS relationship, 'Team' AS source_type, 'System' AS target_type
        }
        RETURN source_id, source, target_id, target, relationship, source_type, target_type
        LIMIT $limit
    """,

    "payment_flow": """
        CALL {
            MATCH (p:BusinessProcess {process_id: 'BP_PAYMENT'})-[r:HAS_STEP]->(step:ProcessStep)
            RETURN p.process_id AS source_id, p.name AS source,
                   step.step_id AS target_id, step.name AS target,
                   'STEP_' + toString(r.sequence) AS relationship,
                   'BusinessProcess' AS source_type, 'ProcessStep' AS target_type,
                   r.sequence AS order_no
            UNION ALL
            MATCH (team:Team)-[:PERFORMS_STEP]->(step:ProcessStep {process_id: 'BP_PAYMENT'})
            RETURN team.team_id AS source_id, team.name AS source,
                   step.step_id AS target_id, step.name AS target,
                   'PERFORMS_STEP' AS relationship,
                   'Team' AS source_type, 'ProcessStep' AS target_type,
                   step.sequence AS order_no
            UNION ALL
            MATCH (step:ProcessStep {process_id: 'BP_PAYMENT'})-[:USES_SYSTEM]->(system:System)
            RETURN step.step_id AS source_id, step.name AS source,
                   system.system_id AS target_id, system.name AS target,
                   'USES_SYSTEM' AS relationship,
                   'ProcessStep' AS source_type, 'System' AS target_type,
                   step.sequence AS order_no
            UNION ALL
            MATCH (control:Control)-[:APPLIES_TO]->(step:ProcessStep {process_id: 'BP_PAYMENT'})
            RETURN control.control_id AS source_id, control.name AS source,
                   step.step_id AS target_id, step.name AS target,
                   'APPLIES_TO' AS relationship,
                   'Control' AS source_type, 'ProcessStep' AS target_type,
                   step.sequence AS order_no
        }
        RETURN source_id, source, target_id, target, relationship, source_type, target_type, order_no
        ORDER BY order_no
        LIMIT $limit
    """,

    "team_interactions": """
        MATCH (source_team:Team)-[r:INTERACTS_WITH]->(target_team:Team)
        RETURN source_team.team_id AS source_id, source_team.name AS source,
               target_team.team_id AS target_id, target_team.name AS target,
               coalesce(r.interaction_type, 'INTERACTS_WITH') AS relationship,
               'Team' AS source_type, 'Team' AS target_type,
               r.description AS evidence_type
        LIMIT $limit
    """,

    "department_employees": """
        CALL {
            MATCH (d:Department)-[:HAS_TEAM]->(t:Team)
            WHERE toLower(d.name) CONTAINS toLower($term)
               OR toLower(d.department_id) = toLower($term)
            RETURN d.department_id AS source_id, d.name AS source,
                   t.team_id AS target_id, t.name AS target,
                   'HAS_TEAM' AS relationship, 'Department' AS source_type, 'Team' AS target_type
            UNION ALL
            MATCH (d:Department)-[:HAS_TEAM]->(t:Team)-[:HAS_EMPLOYEE]->(e:Employee)
            WHERE toLower(d.name) CONTAINS toLower($term)
               OR toLower(d.department_id) = toLower($term)
            RETURN t.team_id AS source_id, t.name AS source,
                   e.employee_id AS target_id, e.name AS target,
                   'HAS_EMPLOYEE' AS relationship, 'Team' AS source_type, 'Employee' AS target_type
        }
        RETURN source_id, source, target_id, target, relationship, source_type, target_type
        LIMIT $limit
    """,

    "system_owners": """
        CALL {
            MATCH (it:Employee)-[:IT_OWNER_OF]->(s:System)
            WHERE toLower(s.name) CONTAINS toLower($term) OR toLower(s.system_id) = toLower($term)
            RETURN it.employee_id AS source_id, it.name AS source,
                   s.system_id AS target_id, s.name AS target,
                   'IT_OWNER_OF' AS relationship, 'Employee' AS source_type, 'System' AS target_type
            UNION ALL
            MATCH (business:Employee)-[:BUSINESS_OWNER_OF]->(s:System)
            WHERE toLower(s.name) CONTAINS toLower($term) OR toLower(s.system_id) = toLower($term)
            RETURN business.employee_id AS source_id, business.name AS source,
                   s.system_id AS target_id, s.name AS target,
                   'BUSINESS_OWNER_OF' AS relationship, 'Employee' AS source_type, 'System' AS target_type
            UNION ALL
            MATCH (team:Team)-[:MANAGES_SYSTEM]->(s:System)
            WHERE toLower(s.name) CONTAINS toLower($term) OR toLower(s.system_id) = toLower($term)
            RETURN team.team_id AS source_id, team.name AS source,
                   s.system_id AS target_id, s.name AS target,
                   'MANAGES_SYSTEM' AS relationship, 'Team' AS source_type, 'System' AS target_type
        }
        RETURN source_id, source, target_id, target, relationship, source_type, target_type
        LIMIT $limit
    """,

    "ownership_search": """
        CALL {
            MATCH (team:Team)-[:MANAGES_SYSTEM]->(s:System)
            WHERE toLower(s.name) CONTAINS toLower($term)
               OR toLower(team.name) CONTAINS toLower($term)
            RETURN team.team_id AS source_id, team.name AS source,
                   s.system_id AS target_id, s.name AS target,
                   'MANAGES_SYSTEM' AS relationship, 'Team' AS source_type, 'System' AS target_type
            UNION ALL
            MATCH (e:Employee)-[r:IT_OWNER_OF|BUSINESS_OWNER_OF]->(s:System)
            WHERE toLower(s.name) CONTAINS toLower($term)
               OR toLower(e.name) CONTAINS toLower($term)
            RETURN e.employee_id AS source_id, e.name AS source,
                   s.system_id AS target_id, s.name AS target,
                   type(r) AS relationship, 'Employee' AS source_type, 'System' AS target_type
        }
        RETURN source_id, source, target_id, target, relationship, source_type, target_type
        LIMIT $limit
    """,

    "employee_search": """
        MATCH (t:Team)-[:HAS_EMPLOYEE]->(e:Employee)
        WHERE toLower(e.name) CONTAINS toLower($term)
           OR toLower(e.role) CONTAINS toLower($term)
           OR toLower(e.task_summary) CONTAINS toLower($term)
        RETURN t.team_id AS source_id, t.name AS source,
               e.employee_id AS target_id, e.name AS target,
               'HAS_EMPLOYEE' AS relationship, 'Team' AS source_type, 'Employee' AS target_type,
               e.role AS role, e.task_summary AS responsibility
        LIMIT $limit
    """,

    "employee_responsibilities": """
        MATCH (e:Employee)-[:RESPONSIBLE_FOR]->(r:Responsibility)
        WHERE toLower(e.name) CONTAINS toLower($term)
           OR toLower(e.role) CONTAINS toLower($term)
           OR toLower(r.name) CONTAINS toLower($term)
           OR toLower(r.category) CONTAINS toLower($term)
        RETURN e.employee_id AS source_id, e.name AS source,
               r.responsibility_id AS target_id, r.name AS target,
               'RESPONSIBLE_FOR' AS relationship, 'Employee' AS source_type, 'Responsibility' AS target_type,
               r.description AS evidence_type
        LIMIT $limit
    """,

    "support_coverage": """
        CALL {
            MATCH (service:Team {team_id:'T_SERVICE'})-[:SUPPORTS_TEAM]->(team:Team)
            RETURN service.team_id AS source_id, service.name AS source,
                   team.team_id AS target_id, team.name AS target,
                   'L1_L2_SUPPORTS' AS relationship, 'Team' AS source_type, 'Team' AS target_type
            UNION ALL
            MATCH (team:Team)-[:USES_SYSTEM]->(ticket:System {system_id:'SYS_TICKET'})
            RETURN team.team_id AS source_id, team.name AS source,
                   ticket.system_id AS target_id, ticket.name AS target,
                   'USES_TICKETING_SYSTEM' AS relationship, 'Team' AS source_type, 'System' AS target_type
        }
        RETURN source_id, source, target_id, target, relationship, source_type, target_type
        LIMIT $limit
    """,

    "access_governance": """
        MATCH (iam:Team {team_id:'T_IAM'})-[:GOVERNS_ACCESS_TO]->(s:System)
        RETURN iam.team_id AS source_id, iam.name AS source,
               s.system_id AS target_id, s.name AS target,
               'GOVERNS_ACCESS_TO' AS relationship, 'Team' AS source_type, 'System' AS target_type
        LIMIT $limit
    """,

    "regulatory_oversight": """
        CALL {
            MATCH (team:Team)-[:MONITORS_FRAMEWORK]->(framework:RegulatoryFramework)
            WHERE toLower(framework.name) CONTAINS toLower($term)
               OR toLower(framework.framework_id) CONTAINS toLower($term)
               OR toLower(team.name) CONTAINS toLower($term)
            RETURN team.team_id AS source_id, team.name AS source,
                   framework.framework_id AS target_id, framework.name AS target,
                   'MONITORS_FRAMEWORK' AS relationship, 'Team' AS source_type, 'RegulatoryFramework' AS target_type
            UNION ALL
            MATCH (framework:RegulatoryFramework)-[:APPLIES_TO]->(s:System)
            WHERE toLower(framework.name) CONTAINS toLower($term)
               OR toLower(framework.framework_id) CONTAINS toLower($term)
               OR toLower($term) IN ['regulatory','oversight','eu']
            RETURN framework.framework_id AS source_id, framework.name AS source,
                   s.system_id AS target_id, s.name AS target,
                   'APPLIES_TO' AS relationship, 'RegulatoryFramework' AS source_type, 'System' AS target_type
        }
        RETURN source_id, source, target_id, target, relationship, source_type, target_type
        LIMIT $limit
    """,

    "data_lineage": """
        CALL {
            MATCH (external:ExternalSource)-[:FEEDS_SYSTEM]->(hub:System {system_id:'SYS_INPUT'})
            RETURN external.source_id AS source_id, external.name AS source,
                   hub.system_id AS target_id, hub.name AS target,
                   'FEEDS_SYSTEM' AS relationship, 'ExternalSource' AS source_type, 'System' AS target_type
            UNION ALL
            MATCH (consumer:System)-[:DEPENDS_ON]->(hub:System {system_id:'SYS_INPUT'})
            RETURN hub.system_id AS source_id, hub.name AS source,
                   consumer.system_id AS target_id, consumer.name AS target,
                   'SUPPLIES_DATA_TO' AS relationship, 'System' AS source_type, 'System' AS target_type
            UNION ALL
            MATCH (hub:System {system_id:'SYS_INPUT'})-[:FEEDS_PIPELINE]->(pipeline:DataPipeline)-[:PRODUCES_DATASET]->(dataset:Dataset)
            RETURN hub.system_id AS source_id, hub.name AS source,
                   pipeline.pipeline_id AS target_id, pipeline.name AS target,
                   'FEEDS_PIPELINE' AS relationship, 'System' AS source_type, 'DataPipeline' AS target_type
            UNION ALL
            MATCH (:System {system_id:'SYS_INPUT'})-[:FEEDS_PIPELINE]->(pipeline:DataPipeline)-[:PRODUCES_DATASET]->(dataset:Dataset)
            RETURN pipeline.pipeline_id AS source_id, pipeline.name AS source,
                   dataset.dataset_id AS target_id, dataset.name AS target,
                   'PRODUCES_DATASET' AS relationship, 'DataPipeline' AS source_type, 'Dataset' AS target_type
        }
        RETURN source_id, source, target_id, target, relationship, source_type, target_type
        LIMIT $limit
    """,

    "process_pipeline": """
        MATCH (p:BusinessProcess)-[r:HAS_STEP]->(step:ProcessStep)
        WHERE toLower(p.name) CONTAINS toLower($term)
           OR toLower(p.process_id) = toLower($term)
        RETURN p.process_id AS source_id, p.name AS source,
               step.step_id AS target_id, step.name AS target,
               'STEP_' + toString(r.sequence) AS relationship,
               'BusinessProcess' AS source_type, 'ProcessStep' AS target_type,
               r.sequence AS step_no
        ORDER BY step_no
        LIMIT $limit
    """,

    "next_step": """
        MATCH (p:BusinessProcess)-[current_link:HAS_STEP]->(current:ProcessStep)
        MATCH (p)-[next_link:HAS_STEP]->(next:ProcessStep)
        WHERE (toLower(current.name) CONTAINS toLower($term)
            OR toLower(current.step_id) = toLower($term))
          AND next_link.sequence = current_link.sequence + 1
        RETURN current.step_id AS source_id, current.name AS source,
               next.step_id AS target_id, next.name AS target,
               'NEXT_STEP' AS relationship, 'ProcessStep' AS source_type, 'ProcessStep' AS target_type
        LIMIT $limit
    """,

    "system_impact": """
        CALL {
            MATCH (dependent:System)-[:DEPENDS_ON]->(failed:System)
            WHERE toLower(failed.name) CONTAINS toLower($term)
               OR toLower(failed.system_id) = toLower($term)
            RETURN failed.system_id AS source_id, failed.name AS source,
                   dependent.system_id AS target_id, dependent.name AS target,
                   'AFFECTS_DEPENDENT_SYSTEM' AS relationship, 'System' AS source_type, 'System' AS target_type
            UNION ALL
            MATCH (process:BusinessProcess)-[:USES_SYSTEM]->(failed:System)
            WHERE toLower(failed.name) CONTAINS toLower($term)
               OR toLower(failed.system_id) = toLower($term)
            RETURN failed.system_id AS source_id, failed.name AS source,
                   process.process_id AS target_id, process.name AS target,
                   'AFFECTS_PROCESS' AS relationship, 'System' AS source_type, 'BusinessProcess' AS target_type
            UNION ALL
            MATCH (step:ProcessStep)-[:USES_SYSTEM]->(failed:System)
            WHERE toLower(failed.name) CONTAINS toLower($term)
               OR toLower(failed.system_id) = toLower($term)
            RETURN failed.system_id AS source_id, failed.name AS source,
                   step.step_id AS target_id, step.name AS target,
                   'AFFECTS_STEP' AS relationship, 'System' AS source_type, 'ProcessStep' AS target_type
        }
        RETURN source_id, source, target_id, target, relationship, source_type, target_type
        LIMIT $limit
    """,

    "missing_owners": """
        MATCH (s:System)
        OPTIONAL MATCH (:Employee)-[it:IT_OWNER_OF]->(s)
        OPTIONAL MATCH (:Employee)-[business:BUSINESS_OWNER_OF]->(s)
        WITH s, count(DISTINCT it) AS it_owners, count(DISTINCT business) AS business_owners
        WHERE it_owners = 0 OR business_owners = 0
        RETURN s.system_id AS source_id, s.name AS source,
               'OWNER_GAP' AS target_id,
               CASE WHEN it_owners = 0 AND business_owners = 0 THEN 'Missing IT and business owner'
                    WHEN it_owners = 0 THEN 'Missing IT owner'
                    ELSE 'Missing business owner' END AS target,
               'OWNER_GAP' AS relationship, 'System' AS source_type, 'Risk' AS target_type
        LIMIT $limit
    """,

    "kpis": """
        CALL {
            MATCH (s:System)
            OPTIONAL MATCH (:Employee)-[it:IT_OWNER_OF]->(s)
            WITH s, count(it) > 0 AS covered
            RETURN count(s) AS total_systems,
                   sum(CASE WHEN covered THEN 1 ELSE 0 END) AS systems_with_it_owner
        }
        CALL {
            MATCH (s:System)
            OPTIONAL MATCH (:Employee)-[owner:BUSINESS_OWNER_OF]->(s)
            WITH s, count(owner) > 0 AS covered
            RETURN sum(CASE WHEN covered THEN 1 ELSE 0 END) AS systems_with_business_owner
        }
        CALL {
            MATCH (team:Team)
            OPTIONAL MATCH (:Team {team_id:'T_SERVICE'})-[support:SUPPORTS_TEAM]->(team)
            WITH team, count(support) > 0 OR team.team_id = 'T_SERVICE' AS covered
            RETURN count(team) AS total_teams,
                   sum(CASE WHEN covered THEN 1 ELSE 0 END) AS teams_with_support
        }
        CALL {
            MATCH (s:System)
            OPTIONAL MATCH (:Team {team_id:'T_IAM'})-[access:GOVERNS_ACCESS_TO]->(s)
            WITH s, count(access) > 0 OR s.system_id = 'SYS_IDM' AS covered
            RETURN sum(CASE WHEN covered THEN 1 ELSE 0 END) AS systems_with_access_governance
        }
        CALL {
            MATCH (p:BusinessProcess)
            OPTIONAL MATCH (p)-[:HAS_STEP]->(:ProcessStep)<-[:APPLIES_TO]-(control:Control)
            WITH p, count(control) > 0 AS covered
            RETURN count(p) AS total_processes,
                   sum(CASE WHEN covered THEN 1 ELSE 0 END) AS covered_processes
        }
        CALL {
            MATCH (step:ProcessStep)
            OPTIONAL MATCH (:Team)-[owner:PERFORMS_STEP]->(step)
            WITH step, count(owner) > 0 AS covered
            RETURN count(step) AS total_steps,
                   sum(CASE WHEN covered THEN 1 ELSE 0 END) AS covered_steps
        }
        RETURN total_systems,
               systems_with_it_owner AS covered_systems,
               round(100.0 * systems_with_it_owner / total_systems, 1) AS system_owner_coverage_pct,
               systems_with_it_owner,
               systems_with_business_owner,
               round(100.0 * systems_with_business_owner / total_systems, 1) AS business_owner_coverage_pct,
               total_teams, teams_with_support,
               round(100.0 * teams_with_support / total_teams, 1) AS support_coverage_pct,
               systems_with_access_governance,
               round(100.0 * systems_with_access_governance / total_systems, 1) AS access_governance_pct,
               total_processes, covered_processes,
               round(100.0 * covered_processes / total_processes, 1) AS process_owner_coverage_pct,
               total_steps, covered_steps,
               round(100.0 * covered_steps / total_steps, 1) AS step_responsibility_pct
    """,

    "concept_dataset": """
        MATCH (d:Dataset)-[:USED_BY_SYSTEM|USED_BY_PROCESS]->(consumer)
        RETURN d.dataset_id AS source_id, d.name AS source,
               coalesce(consumer.system_id, consumer.process_id) AS target_id, consumer.name AS target,
               'USED_BY' AS relationship, 'Dataset' AS source_type, labels(consumer)[0] AS target_type
        LIMIT $limit
    """,

    "concept_system": """
        MATCH (team:Team)-[:MANAGES_SYSTEM]->(system:System)
        RETURN team.team_id AS source_id, team.name AS source,
               system.system_id AS target_id, system.name AS target,
               'MANAGES_SYSTEM' AS relationship, 'Team' AS source_type, 'System' AS target_type
        LIMIT $limit
    """,

    "concept_business_process": """
        MATCH (p:BusinessProcess)-[:HAS_STEP]->(step:ProcessStep)
        RETURN p.process_id AS source_id, p.name AS source,
               step.step_id AS target_id, step.name AS target,
               'HAS_STEP' AS relationship, 'BusinessProcess' AS source_type, 'ProcessStep' AS target_type
        LIMIT $limit
    """,

    "concept_data_pipeline": """
        MATCH (pipeline:DataPipeline)-[:PRODUCES_DATASET]->(dataset:Dataset)
        RETURN pipeline.pipeline_id AS source_id, pipeline.name AS source,
               dataset.dataset_id AS target_id, dataset.name AS target,
               'PRODUCES_DATASET' AS relationship, 'DataPipeline' AS source_type, 'Dataset' AS target_type
        LIMIT $limit
    """,

    "entity_catalog": """
        MATCH (n)
        WHERE any(label IN labels(n) WHERE label IN $labels)
        RETURN labels(n)[0] AS label,
               coalesce(n.department_id, n.team_id, n.employee_id, n.system_id, n.source_id,
                        n.framework_id, n.control_id, n.responsibility_id, n.project_id,
                        n.process_id, n.step_id, n.pipeline_id, n.dataset_id) AS node_id,
               n.name AS name,
               coalesce(n.description, n.task_summary, n.role, '') AS description
        ORDER BY label, name
        LIMIT $limit
    """,

    "global_search": """
        MATCH (matched)
        WHERE any(label IN labels(matched) WHERE label IN $labels)
          AND (
            toLower(coalesce(matched.name, '')) CONTAINS toLower($term)
            OR any(key IN keys(matched)
                   WHERE toLower(toString(matched[key])) CONTAINS toLower($term))
          )
        MATCH (matched)-[r]-(connected)
        WHERE any(label IN labels(connected) WHERE label IN $labels)
        RETURN coalesce(matched.department_id, matched.team_id, matched.employee_id, matched.system_id,
                        matched.source_id, matched.framework_id, matched.control_id, matched.responsibility_id,
                        matched.project_id, matched.process_id, matched.step_id, matched.pipeline_id, matched.dataset_id) AS source_id,
               matched.name AS source,
               coalesce(connected.department_id, connected.team_id, connected.employee_id, connected.system_id,
                        connected.source_id, connected.framework_id, connected.control_id, connected.responsibility_id,
                        connected.project_id, connected.process_id, connected.step_id, connected.pipeline_id, connected.dataset_id) AS target_id,
               connected.name AS target,
               type(r) AS relationship,
               labels(matched)[0] AS source_type,
               labels(connected)[0] AS target_type
        LIMIT $limit
    """
}
