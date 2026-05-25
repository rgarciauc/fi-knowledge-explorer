#!/usr/bin/env bash
set -euo pipefail

echo "=== Ollama status from backend network ==="
curl -fsS http://localhost:8000/api/llm/status | python3 -m json.tool
echo

echo "=== System owners: Sanctions Monitoring ==="
curl -fsS -X POST http://localhost:8000/api/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"Who are the IT and business owners of Sanctions Monitoring?"}' \
  | python3 -c '
import json,sys
d=json.load(sys.stdin)
print("intent:", d["intent"])
print("template:", d["query_trace"]["template"])
print("term:", d["query_trace"]["resolved_term"])
print("rows:", [(r["relationship"], r["source"], r["target"]) for r in d["rows"]])
assert d["query_trace"]["template"] == "system_owners"
assert d["query_trace"]["resolved_term"] == "Sanctions Monitoring"
assert len(d["rows"]) <= 4
'
echo

echo "=== System impact: Sanctions Monitoring ==="
curl -fsS -X POST http://localhost:8000/api/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"What is affected if Sanctions Monitoring fails?"}' \
  | python3 -c '
import json,sys
d=json.load(sys.stdin)
rels={r["relationship"] for r in d["rows"]}
print("intent:", d["intent"])
print("template:", d["query_trace"]["template"])
print("term:", d["query_trace"]["resolved_term"])
print("relationships:", sorted(rels))
print("presentation:", d["graph"].get("presentation"))
assert d["query_trace"]["template"] == "system_impact"
assert d["query_trace"]["resolved_term"] == "Sanctions Monitoring"
assert "IMPACTS_DEPENDENT_SYSTEM" in rels
'
echo

echo "=== Responsibilities: Amira Haddad ==="
curl -fsS -X POST http://localhost:8000/api/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"What responsibilities does Amira Haddad have?"}' \
  | python3 -c '
import json,sys
d=json.load(sys.stdin)
print("rows:", [(r["relationship"], r["target"]) for r in d["rows"]])
rels={r["relationship"] for r in d["rows"]}
assert "IT_OWNER_OF" in rels
assert "LEADS_TEAM" in rels
'
echo
echo "All deterministic answer-route checks passed."
