#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi

PASSWORD="${NEO4J_PASSWORD:-SuperBank_ChangeMe_2026}"

echo "Ensuring Neo4j is running..."
docker compose up -d neo4j

echo "Loading CSV data through the idempotent importer..."
docker compose run --rm neo4j-import

echo
echo "Node counts:"
docker exec super_bank_neo4j cypher-shell -u neo4j -p "$PASSWORD" \
  "MATCH (n) RETURN labels(n)[0] AS label, count(*) AS total ORDER BY label;"

echo
echo "Systems without ownership:"
docker exec super_bank_neo4j cypher-shell -u neo4j -p "$PASSWORD" \
  "MATCH (s:System) WHERE NOT (:Team)-[:OWNS_SYSTEM]->(s) RETURN s.system_id AS system_id, s.name AS system;"

echo
echo "Systems with more than one owning team (review ownership intent):"
docker exec super_bank_neo4j cypher-shell -u neo4j -p "$PASSWORD" \
  "MATCH (t:Team)-[:OWNS_SYSTEM]->(s:System) WITH s, collect(t.name) AS teams WHERE size(teams) > 1 RETURN s.system_id AS system_id, s.name AS system, teams;"
