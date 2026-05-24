"""Read-only queries aligned with data/neo4j_starter/cypher/import.cypher.

The starter graph uses BusinessProcess, OWNS_SYSTEM, PERFORMS_STEP,
RESPONSIBLE_FOR_STEP, FEEDS_PIPELINE and PRODUCES_DATASET.  It does not contain
the alternative Process/IT_OWNER_OF/BUSINESS_OWNER_OF/DEPENDS_ON model.
"""

QUERY_TEMPLATES = {

    "department_employees": """
        CALL {
            MATCH (d:Department)-[:HAS_TEAM]->(t:Team)
            WHERE toLower(d.name) CONTAINS toLower($term)
               OR toLower(d.department_id) = toLower($term)
            RETURN d.department_id AS source_id, d.name AS source,
                   t.team_id AS target_id, t.name AS target,
                   'HAS_TEAM' AS relationship,
                   'Department' AS source_type, 'Team' AS target_type
            UNION ALL
            MATCH (d:Department)-[:HAS_TEAM]->(t:Team)-[:HAS_EMPLOYEE]->(e:Employee)
            WHERE toLower(d.name) CONTAINS toLower($term)
               OR toLower(d.department_id) = toLower($term)
            RETURN t.team_id AS source_id, t.name AS source,
                   e.employee_id AS target_id, e.name AS target,
                   'HAS_EMPLOYEE' AS relationship,
                   'Team' AS source_type, 'Employee' AS target_type
        }
        RETURN source_id, source, target_id, target, relationship, source_type, target_type
        LIMIT $limit
    """,


    "concept_dataset": """
        MATCH (d:Dataset)-[:USED_BY_PROCESS]->(p:BusinessProcess)
        RETURN d.dataset_id AS source_id, d.name AS source,
               p.process_id AS target_id, p.name AS target,
               'USED_BY_PROCESS' AS relationship,
               'Dataset' AS source_type, 'BusinessProcess' AS target_type,
               'A dataset supplies evidence or information used by a process.' AS evidence_type
        LIMIT $limit
    """,

    "concept_system": """
        MATCH (s:System)-[:FEEDS_PIPELINE]->(p:DataPipeline)
        RETURN s.system_id AS source_id, s.name AS source,
               p.pipeline_id AS target_id, p.name AS target,
               'FEEDS_PIPELINE' AS relationship,
               'System' AS source_type, 'DataPipeline' AS target_type,
               'A system provides operational or data input.' AS evidence_type
        LIMIT $limit
    """,

    "concept_business_process": """
        MATCH (p:BusinessProcess)-[:HAS_STEP]->(s:ProcessStep)
        RETURN p.process_id AS source_id, p.name AS source,
               s.step_id AS target_id, s.name AS target,
               'HAS_STEP' AS relationship,
               'BusinessProcess' AS source_type, 'ProcessStep' AS target_type,
               'A business process is performed through ordered steps.' AS evidence_type
        LIMIT $limit
    """,

    "concept_data_pipeline": """
        MATCH (p:DataPipeline)-[:PRODUCES_DATASET]->(d:Dataset)
        RETURN p.pipeline_id AS source_id, p.name AS source,
               d.dataset_id AS target_id, d.name AS target,
               'PRODUCES_DATASET' AS relationship,
               'DataPipeline' AS source_type, 'Dataset' AS target_type,
               'A data pipeline produces datasets from source-system input.' AS evidence_type
        LIMIT $limit
    """,

    "overview": """
        MATCH (d:Department)-[:HAS_TEAM]->(t:Team)
        RETURN d.department_id AS source_id, d.name AS source,
               t.team_id AS target_id, t.name AS target,
               'HAS_TEAM' AS relationship,
               'Department' AS source_type, 'Team' AS target_type
        UNION ALL
        MATCH (t:Team)-[:HAS_EMPLOYEE]->(e:Employee)
        RETURN t.team_id AS source_id, t.name AS source,
               e.employee_id AS target_id, e.name AS target,
               'HAS_EMPLOYEE' AS relationship,
               'Team' AS source_type, 'Employee' AS target_type
        LIMIT $limit
    """,

    "ownership_search": """
        MATCH (t:Team)-[:OWNS_SYSTEM]->(s:System)
        WHERE toLower(s.name) CONTAINS toLower($term)
           OR toLower(s.system_id) = toLower($term)
           OR toLower(t.name) CONTAINS toLower($term)
        OPTIONAL MATCH (d:Department)-[:HAS_TEAM]->(t)
        RETURN 'System' AS entity_type, s.name AS entity, t.name AS owner,
               d.name AS owner_department,
               t.team_id AS source_id, t.name AS source,
               s.system_id AS target_id, s.name AS target,
               'OWNS_SYSTEM' AS relationship,
               'Team' AS source_type, 'System' AS target_type
        UNION ALL
        MATCH (e:Employee)-[:OWNS_PROCESS]->(p:BusinessProcess)
        WHERE toLower(p.name) CONTAINS toLower($term)
           OR toLower(p.process_id) = toLower($term)
           OR toLower(e.name) CONTAINS toLower($term)
        OPTIONAL MATCH (t:Team)-[:HAS_EMPLOYEE]->(e)
        RETURN 'BusinessProcess' AS entity_type, p.name AS entity, e.name AS owner,
               t.name AS owner_department,
               e.employee_id AS source_id, e.name AS source,
               p.process_id AS target_id, p.name AS target,
               'OWNS_PROCESS' AS relationship,
               'Employee' AS source_type, 'BusinessProcess' AS target_type
        LIMIT $limit
    """,

    "responsibilities_overview": """
        MATCH (t:Team)-[:OWNS_SYSTEM]->(s:System)
        RETURN t.team_id AS source_id, t.name AS source,
               s.system_id AS target_id, s.name AS target,
               'OWNS_SYSTEM' AS relationship,
               'Team' AS source_type, 'System' AS target_type
        UNION ALL
        MATCH (e:Employee)-[:OWNS_PROCESS]->(p:BusinessProcess)
        RETURN e.employee_id AS source_id, e.name AS source,
               p.process_id AS target_id, p.name AS target,
               'OWNS_PROCESS' AS relationship,
               'Employee' AS source_type, 'BusinessProcess' AS target_type
        LIMIT $limit
    """,

    "employee_search": """
        MATCH (t:Team)-[:HAS_EMPLOYEE]->(e:Employee)
        WHERE toLower(e.name) CONTAINS toLower($term)
           OR toLower(e.role) CONTAINS toLower($term)
           OR toLower(e.task_summary) CONTAINS toLower($term)
        RETURN e.name AS employee, e.role AS role, e.task_summary AS responsibility,
               t.team_id AS source_id, t.name AS source,
               e.employee_id AS target_id, e.name AS target,
               'HAS_EMPLOYEE' AS relationship,
               'Team' AS source_type, 'Employee' AS target_type
        LIMIT $limit
    """,

    "process_pipeline": """
        MATCH (p:BusinessProcess)-[link:HAS_STEP]->(step:ProcessStep)
        WHERE toLower(p.name) CONTAINS toLower($term)
           OR toLower(p.process_id) = toLower($term)
        OPTIONAL MATCH (owner:Employee)-[:RESPONSIBLE_FOR_STEP]->(step)
        OPTIONAL MATCH (team:Team)-[:PERFORMS_STEP]->(step)
        WITH p, link, step, owner, team
        ORDER BY link.sequence
        RETURN p.name AS process, link.sequence AS step_no, step.name AS step,
               owner.name AS responsible_employee, team.name AS responsible_team,
               p.process_id AS source_id, p.name AS source,
               step.step_id AS target_id, step.name AS target,
               'HAS_STEP' AS relationship,
               'BusinessProcess' AS source_type, 'ProcessStep' AS target_type
        ORDER BY step_no
        LIMIT $limit
    """,

    "next_step": """
        MATCH (p:BusinessProcess)-[current_link:HAS_STEP]->(current:ProcessStep)
        MATCH (p)-[next_link:HAS_STEP]->(next:ProcessStep)
        WHERE (toLower(current.name) CONTAINS toLower($term)
           OR toLower(current.step_id) = toLower($term))
          AND next_link.sequence = current_link.sequence + 1
        OPTIONAL MATCH (e:Employee)-[:RESPONSIBLE_FOR_STEP]->(next)
        OPTIONAL MATCH (t:Team)-[:PERFORMS_STEP]->(next)
        RETURN p.name AS process, current.name AS current_step, next.name AS next_step,
               e.name AS responsible_employee, t.name AS responsible_team,
               current.step_id AS source_id, current.name AS source,
               next.step_id AS target_id, next.name AS target,
               'NEXT_STEP_BY_SEQUENCE' AS relationship,
               'ProcessStep' AS source_type, 'ProcessStep' AS target_type
        LIMIT $limit
    """,

    "system_impact": """
        CALL {
            MATCH (failed:System)
            WHERE toLower(failed.name) CONTAINS toLower($term)
               OR toLower(failed.system_id) = toLower($term)
            MATCH (p:BusinessProcess)-[:USES_SYSTEM]->(failed)
            RETURN failed.system_id AS source_id, failed.name AS source,
                   p.process_id AS target_id, p.name AS target,
                   'SUPPORTS_PROCESS' AS relationship,
                   'System' AS source_type, 'BusinessProcess' AS target_type,
                   'Direct process usage' AS impact_type
            UNION ALL
            MATCH (failed:System)
            WHERE toLower(failed.name) CONTAINS toLower($term)
               OR toLower(failed.system_id) = toLower($term)
            MATCH (failed)-[:FEEDS_PIPELINE]->(pipeline:DataPipeline)
            RETURN failed.system_id AS source_id, failed.name AS source,
                   pipeline.pipeline_id AS target_id, pipeline.name AS target,
                   'FEEDS_PIPELINE' AS relationship,
                   'System' AS source_type, 'DataPipeline' AS target_type,
                   'Data pipeline input' AS impact_type
            UNION ALL
            MATCH (failed:System)
            WHERE toLower(failed.name) CONTAINS toLower($term)
               OR toLower(failed.system_id) = toLower($term)
            MATCH (failed)-[:FEEDS_PIPELINE]->(:DataPipeline)-[:PRODUCES_DATASET]->(dataset:Dataset)
            RETURN failed.system_id AS source_id, failed.name AS source,
                   dataset.dataset_id AS target_id, dataset.name AS target,
                   'PRODUCES_AFFECTED_DATASET' AS relationship,
                   'System' AS source_type, 'Dataset' AS target_type,
                   'Dataset derived from failed system' AS impact_type
            UNION ALL
            MATCH (failed:System)
            WHERE toLower(failed.name) CONTAINS toLower($term)
               OR toLower(failed.system_id) = toLower($term)
            MATCH (failed)-[:FEEDS_PIPELINE]->(:DataPipeline)-[:PRODUCES_DATASET]->(:Dataset)-[:USED_BY_PROCESS]->(p:BusinessProcess)
            RETURN failed.system_id AS source_id, failed.name AS source,
                   p.process_id AS target_id, p.name AS target,
                   'AFFECTS_PROCESS_VIA_DATA' AS relationship,
                   'System' AS source_type, 'BusinessProcess' AS target_type,
                   'Downstream dataset dependency' AS impact_type
        }
        RETURN source_id, source, target_id, target, relationship,
               source_type, target_type, impact_type
        LIMIT $limit
    """,

    "missing_owners": """
        MATCH (s:System)
        OPTIONAL MATCH (t:Team)-[:OWNS_SYSTEM]->(s)
        WITH s, count(t) AS owner_team_count
        WHERE owner_team_count = 0
        RETURN s.name AS system, owner_team_count,
               s.system_id AS source_id, s.name AS source,
               'OWNER_GAP' AS target_id, 'Missing owning team' AS target,
               'GAP' AS relationship,
               'System' AS source_type, 'Risk' AS target_type
        LIMIT $limit
    """,

    "kpis": """
        CALL {
            MATCH (s:System)
            OPTIONAL MATCH (:Team)-[owner:OWNS_SYSTEM]->(s)
            WITH s, count(owner) > 0 AS covered
            RETURN count(s) AS total_systems,
                   sum(CASE WHEN covered THEN 1 ELSE 0 END) AS covered_systems
        }
        CALL {
            MATCH (p:BusinessProcess)
            OPTIONAL MATCH (:Employee)-[owner:OWNS_PROCESS]->(p)
            WITH p, count(owner) > 0 AS covered
            RETURN count(p) AS total_processes,
                   sum(CASE WHEN covered THEN 1 ELSE 0 END) AS covered_processes
        }
        CALL {
            MATCH (step:ProcessStep)
            OPTIONAL MATCH (:Employee)-[owner:RESPONSIBLE_FOR_STEP]->(step)
            WITH step, count(owner) > 0 AS covered
            RETURN count(step) AS total_steps,
                   sum(CASE WHEN covered THEN 1 ELSE 0 END) AS covered_steps
        }
        RETURN total_systems, covered_systems,
               round(100.0 * covered_systems / total_systems, 1) AS system_owner_coverage_pct,
               total_processes, covered_processes,
               round(100.0 * covered_processes / total_processes, 1) AS process_owner_coverage_pct,
               total_steps, covered_steps,
               round(100.0 * covered_steps / total_steps, 1) AS step_responsibility_pct
    """,

    "entity_catalog": """
        MATCH (n)
        WHERE any(label IN labels(n) WHERE label IN $labels)
        RETURN labels(n)[0] AS label,
               coalesce(n.department_id, n.team_id, n.employee_id, n.system_id,
                        n.project_id, n.process_id, n.step_id, n.pipeline_id,
                        n.dataset_id) AS node_id,
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
        OPTIONAL MATCH (matched)-[r]-(connected)
        WITH matched, r, connected
        WHERE r IS NOT NULL AND any(label IN labels(connected) WHERE label IN $labels)
        RETURN coalesce(matched.department_id, matched.team_id, matched.employee_id,
                        matched.system_id, matched.project_id, matched.process_id,
                        matched.step_id, matched.pipeline_id, matched.dataset_id) AS source_id,
               matched.name AS source,
               coalesce(connected.department_id, connected.team_id, connected.employee_id,
                        connected.system_id, connected.project_id, connected.process_id,
                        connected.step_id, connected.pipeline_id, connected.dataset_id) AS target_id,
               connected.name AS target,
               type(r) AS relationship,
               labels(matched)[0] AS source_type,
               labels(connected)[0] AS target_type,
               'Global neighborhood evidence' AS evidence_type
        LIMIT $limit
    """

}
