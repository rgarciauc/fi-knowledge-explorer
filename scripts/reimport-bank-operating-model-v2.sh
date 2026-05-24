#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "Re-importing Bank Operating Model v2 additions/property updates without resetting Neo4j..."
docker compose up -d neo4j
docker compose run --rm neo4j-import

PASSWORD="${NEO4J_PASSWORD:-SuperBank_ChangeMe_2026}"
echo "Ownership gaps:"
docker exec super_bank_neo4j cypher-shell -u neo4j -p "$PASSWORD" \
  "MATCH (s:System) WHERE NOT (:Employee)-[:IT_OWNER_OF]->(s) OR NOT (:Employee)-[:BUSINESS_OWNER_OF]->(s) RETURN s.system_id, s.name;"

echo "Completed. For removals or identity changes, use a reviewed migration or a clean development activation."
