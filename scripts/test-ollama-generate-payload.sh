#!/usr/bin/env bash
set -euo pipefail

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

docker compose exec backend python - <<'PY'
import os
import httpx

url = os.environ.get("LLM_URL", "http://ollama:11434/api/generate")
model = os.environ.get("LLM_MODEL", "llama3.2:3b")

with httpx.Client(timeout=120.0, trust_env=False) as client:
    for value in ("-1", -1, "-1m", "5m"):
        response = client.post(
            url,
            json={
                "model": model,
                "prompt": "Reply only with OK.",
                "stream": False,
                "keep_alive": value,
                "options": {"temperature": 0.0},
            },
        )
        print(f"keep_alive={value!r}: status={response.status_code}, body={response.text[:300]!r}")
PY
