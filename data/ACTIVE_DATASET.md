# Active Neo4j dataset — Bank Operating Model v2

The intended active data source is now:

```text
data/bank_operating_model_v2/import/
data/bank_operating_model_v2/cypher/import.cypher
```

The prior starter model remains historical/deprecated for this application generation:

```text
data/neo4j_starter/
```

Do not import both into the same live development database. The models overlap on labels while differing materially in systems, ownership, processes, controls and regulatory relationships.

## Activation requirement

Because the previous graph was already imported into the Neo4j named volume, switching the Compose mounts alone is not enough. For a clean development activation, intentionally reset only the Neo4j volume and load v2:

```bash
./scripts/activate-bank-operating-model-v2.sh
```

Ollama model storage is preserved by that script.
