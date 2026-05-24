// Safe, read-only checks for the starter-compatible application.

// Imported node counts.
MATCH (n)
RETURN labels(n)[0] AS label, count(*) AS total
ORDER BY label;

// System ownership data used by "Who owns system EMBARGO?"
MATCH (t:Team)-[:OWNS_SYSTEM]->(s:System {name: 'EMBARGO'})
RETURN t.name AS owning_team, s.name AS system;

// Process pipeline used by "Show the pipeline for Payment Processing".
MATCH (p:BusinessProcess {name: 'Payment Processing'})-[r:HAS_STEP]->(s:ProcessStep)
RETURN p.name AS process, r.sequence AS step_no, s.name AS step
ORDER BY step_no;

// Next step derived from the HAS_STEP relationship sequence.
MATCH (p:BusinessProcess)-[a:HAS_STEP]->(current:ProcessStep)
MATCH (p)-[b:HAS_STEP]->(next:ProcessStep)
WHERE current.name CONTAINS 'Receive trigger/input - Payment Processing'
  AND b.sequence = a.sequence + 1
RETURN current.name AS current_step, next.name AS next_step;

// Pipeline/dataset impact path for EMBARGO.
MATCH path=(s:System {name: 'EMBARGO'})-[:FEEDS_PIPELINE]->(:DataPipeline)
          -[:PRODUCES_DATASET]->(:Dataset)-[:USED_BY_PROCESS]->(:BusinessProcess)
RETURN path;
