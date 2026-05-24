# SUPER_BANK Knowledge Graph — Bank Operating Model v2 Overlay

This overlay changes the application from the starter seed graph to a bank operating model that explicitly represents payment routing, team collaboration, system accountability, operational controls, service support, identity governance, data lineage and regulatory oversight.

## Important: this is a model migration

The former active data source:

```text
data/neo4j_starter/
```

is not extended in place. It is retained as historical seed content.

The new source is:

```text
data/bank_operating_model_v2/import/
data/bank_operating_model_v2/cypher/import.cypher
```

The supplied `docker-compose.yml` switches Neo4j import mounts to v2.

## What is modeled

```text
IT Payments → IT Compliance → IT Payments → Settlement & Reconciliation → payment status update
IT Compliance → Sanctions Monitoring and Compliance Market Abuse Surveillance
Data Integration → Input Hub System → compliance feed dependencies
IT Service Desk → L1/L2 support for operational teams
Ticketing Systems Team → Ticketing System used by teams
Identity Management → access governance for managed systems
EU Regulatory Office → DORA and GDPR oversight links
Employee → IT_OWNER_OF / BUSINESS_OWNER_OF → System
Employee → RESPONSONSIBLE_FOR → Responsibility
```

## Apply the files safely

From the parent directory containing your real project:

```bash
cd /Users/rubengarcia/Documents/ki2
unzip ~/Downloads/super-bank-operating-model-v2-overlay.zip

chmod +x super-bank-operating-model-v2-overlay/apply-operating-model-v2.sh
./super-bank-operating-model-v2-overlay/apply-operating-model-v2.sh \
  /Users/rubengarcia/Documents/ki2/financial-institution-knowledge-explorer
```

The installer backs up replaced files and copies v2 files. It does **not** delete your Neo4j volume.

## Activate the new graph data

Because the old Neo4j volume contains the old schema/data, clean development activation is intentionally separate and explicit:

```bash
cd /Users/rubengarcia/Documents/ki2/financial-institution-knowledge-explorer
./scripts/activate-bank-operating-model-v2.sh
```

When asked, type:

```text
ACTIVATE_V2
```

That script removes only the Neo4j data volume, then imports the v2 source and rebuilds backend/frontend. It preserves the Ollama model volume.

## Run after later additions or name edits

After v2 is active, for additive rows or property/name changes that keep stable IDs:

```bash
./scripts/reimport-bank-operating-model-v2.sh
docker compose up -d --build backend frontend
```

For removals or ID changes, use a reviewed migration or re-activate a clean development database.

## Validate in the browser

Open:

```text
http://localhost:3000
```

Recommended questions:

```text
Show the end-to-end payment flow and GO or NO-GO decision
How do the IT Payments and IT Compliance teams interact?
Who are the IT and business owners of Sanctions Monitoring?
Who works in the IT Compliance Department?
What systems depend on the Input Hub System?
How does the IT Service Desk support all teams?
Which systems are governed by Identity Management?
Which systems are under DORA oversight?
What responsibilities does Amira Haddad have?
What is affected if Sanctions Monitoring fails?
Show KPI summary
```

## Validate through the API

```bash
curl -sS -X POST http://localhost:8000/api/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"Show the end-to-end payment flow and GO or NO-GO decision"}' \
  | python3 -m json.tool

curl -sS -X POST http://localhost:8000/api/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"Who are the IT and business owners of Sanctions Monitoring?"}' \
  | python3 -m json.tool

curl -sS -X POST http://localhost:8000/api/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"Which systems are under DORA oversight?"}' \
  | python3 -m json.tool
```

## Files included

```text
docker-compose.yml
PIPELINE.md
data/ACTIVE_DATASET.md
data/bank_operating_model_v2/README.md
data/bank_operating_model_v2/cypher/import.cypher
data/bank_operating_model_v2/import/*.csv

backend/app/graph_schema.py
backend/app/schema_context.py
backend/app/intent_models.py
backend/app/entity_resolution.py
backend/app/intent_detector.py
backend/app/query_templates.py
backend/app/service.py
backend/app/db.py
backend/app/routes.py
backend/app/cypher_generator.py
backend/tests/test_operating_model_v2.py

frontend/app/utils/graphPresentation.ts
frontend/app/utils/api.ts
frontend/app/components/KpiDashboard.vue
frontend/app/components/EvidencePanel.vue

docs/BANK_OPERATING_MODEL_V2.md
scripts/activate-bank-operating-model-v2.sh
scripts/reimport-bank-operating-model-v2.sh
apply-operating-model-v2.sh
```
