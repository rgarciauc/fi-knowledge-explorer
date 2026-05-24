#!/usr/bin/env sh
set -eu

mkdir -p logs/diagnostics
timestamp="$(date '+%Y%m%d-%H%M%S')"
report="logs/diagnostics/report-${timestamp}.txt"

{
  echo "SUPER_BANK diagnostic report - ${timestamp}"
  echo
  echo "=== docker compose ps ==="
  docker compose ps || true
  echo
  echo "=== backend health ==="
  curl -sS -i http://localhost:8000/health || true
  echo
  echo
  echo "=== frontend -> backend proxy examples ==="
  curl -sS -i http://localhost:3000/api/examples || true
  echo
  echo
  echo "=== ollama models ==="
  curl -sS -i http://localhost:11434/api/tags || true
  echo
  echo
  echo "=== recent Docker service logs ==="
  docker compose logs --tail=80 neo4j neo4j-import ollama ollama-init backend frontend || true
} > "${report}" 2>&1

echo "Wrote diagnostic report to ${report}"
