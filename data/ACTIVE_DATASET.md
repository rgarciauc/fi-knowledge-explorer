# Active Neo4j dataset

The database currently loaded by the user came from:

```text
data/neo4j_starter/import/
data/neo4j_starter/cypher/import.cypher
```

That is the **active source dataset** for this compatibility-fixed project.

The files formerly under `data/csv/` use a different schema (`Process`,
`IT_OWNER_OF`, `DEPENDS_ON`, controls/risks). They have been preserved in:

```text
data/alternate_model_not_loaded/csv/
```

They are not used by the backend or the active Neo4j loader.

## Why this is necessary

The loaded starter graph contains:

```text
BusinessProcess
DataPipeline
Dataset
OWNS_SYSTEM
FEEDS_PIPELINE
PRODUCES_DATASET
USED_BY_PROCESS
RESPONSIBLE_FOR_STEP
PERFORMS_STEP
```

The alternate CSV model expected:

```text
Process
IT_OWNER_OF / BUSINESS_OWNER_OF
DEPENDS_ON
NEXT_STEP
Control
Risk
```

Do not mix both models in one Neo4j database until a deliberate migration has been designed.

## Start the already-loaded Neo4j database

```bash
docker compose -f data/neo4j_starter/docker-compose.yml up -d
```

The starter import uses `MERGE`, so re-running its import against the same
database is idempotent for the relationships it defines. It does not load the
alternate model.

## Verify what is loaded

```cypher
MATCH (n)
RETURN labels(n)[0] AS label, count(*) AS total
ORDER BY label;
```
