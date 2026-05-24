#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if [ ! -f "data/bank_operating_model_v2/cypher/import.cypher" ]; then
  echo "Error: v2 importer not found. Apply the operating-model overlay first." >&2
  exit 1
fi

echo "This will replace the local Neo4j graph database with Bank Operating Model v2."
echo "It deletes only the Neo4j named volume; the Ollama model volume is preserved."
echo "Any changes made only inside Neo4j and not represented in CSV/Cypher will be lost."
read -r -p "Type ACTIVATE_V2 to continue: " confirmation
if [ "$confirmation" != "ACTIVATE_V2" ]; then
  echo "Cancelled."
  exit 1
fi

mkdir -p logs/neo4j logs/backend logs/frontend logs/diagnostics

echo "Stopping graph-dependent services..."
docker compose stop frontend backend neo4j-import neo4j || true
docker compose rm -sf frontend backend neo4j-import neo4j || true

echo "Removing previous Neo4j data volume..."
docker volume rm super-bank_neo4j_data 2>/dev/null || true

echo "Starting clean Neo4j and importing Bank Operating Model v2..."
docker compose up -d neo4j
docker compose run --rm neo4j-import

echo "Starting backend and frontend..."
docker compose up -d --build backend frontend

echo "Validating model version and core relationships..."
PASSWORD="${NEO4J_PASSWORD:-SuperBank_ChangeMe_2026}"
docker exec super_bank_neo4j cypher-shell -u neo4j -p "$PASSWORD" \
  "MATCH (n) WHERE n.model_version='v2' RETURN labels(n)[0] AS label, count(*) AS total ORDER BY label;"

docker exec super_bank_neo4j cypher-shell -u neo4j -p "$PASSWORD" \
  "MATCH (:Team {team_id:'T_PAY_IT'})-[r:INTERACTS_WITH]->(:Team {team_id:'T_COMP_IT'}) RETURN type(r), r.interaction_type;"

docker exec super_bank_neo4j cypher-shell -u neo4j -p "$PASSWORD" \
  "MATCH (it:Employee)-[:IT_OWNER_OF]->(s:System)<-[:BUSINESS_OWNER_OF]-(business:Employee) RETURN s.name, it.name, business.name ORDER BY s.name;"

echo "Bank Operating Model v2 activation complete."
echo "Open http://localhost:3000 and try the new example questions."
