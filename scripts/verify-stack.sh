#!/usr/bin/env bash
set -euo pipefail

PASSWORD="${NEO4J_PASSWORD:-SuperBank_ChangeMe_2026}"

echo "Backend health:"
curl -fsS http://localhost:8000/health && echo

echo "Ollama models:"
curl -fsS http://localhost:11434/api/tags && echo

echo "Neo4j imported node counts:"
docker exec super_bank_neo4j cypher-shell -u neo4j -p "$PASSWORD" \
  'MATCH (n) RETURN labels(n)[0] AS label, count(*) AS total ORDER BY label;'

echo "Application example query:"
curl -fsS -X POST http://localhost:8000/api/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"Who owns system EMBARGO?"}' && echo
