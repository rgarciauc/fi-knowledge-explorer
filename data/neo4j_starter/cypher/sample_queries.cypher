// Count imported entities by type
MATCH (n)
RETURN labels(n)[0] AS entity_type, count(*) AS total
ORDER BY entity_type;

// Visual sample: departments, teams and employees
MATCH path=(d:Department)-[:HAS_TEAM]->(t:Team)-[:HAS_EMPLOYEE]->(e:Employee)
RETURN path
LIMIT 50;

// Who owns processes and which systems do they use?
MATCH (d:Department)-[:OWNS_PROCESS]->(p:BusinessProcess)-[:USES_SYSTEM]->(s:System)
RETURN d.name AS department, p.name AS process, s.name AS system
ORDER BY department, process;

// Explore process steps in order
MATCH (p:BusinessProcess)-[r:HAS_STEP]->(s:ProcessStep)
RETURN p.name AS process, r.sequence AS sequence, s.name AS step, s.sla_hours AS sla_hours
ORDER BY process, sequence;

// Impact analysis: systems feeding pipelines producing datasets used by processes
MATCH path=(s:System)-[:FEEDS_PIPELINE]->(:DataPipeline)-[:PRODUCES_DATASET]->(:Dataset)-[:USED_BY_PROCESS]->(:BusinessProcess)
RETURN path
LIMIT 50;

// Projects and affected systems
MATCH (pr:Project)-[r:USES_SYSTEM]->(s:System)
RETURN pr.name AS project, s.name AS system, r.dependency_level AS dependency
ORDER BY dependency DESC, project;
