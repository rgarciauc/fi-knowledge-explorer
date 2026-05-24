# Logging and error diagnostics

This overlay adds request-correlated application logging. It keeps the graph schema and CSV data unchanged.

## Apply

Copy these files into the repository root, preserving directories. Then prepare host log directories:

```bash
mkdir -p logs/neo4j logs/backend logs/frontend logs/containers logs/diagnostics
chmod ugo+rwx logs/neo4j logs/backend logs/frontend
chmod +x scripts/capture-logs.sh scripts/diagnose.sh
```

The permissive directory permission is intended for local development so the Docker containers can write log files on macOS/Linux. Do not copy that permission policy to a production server without defining container users and ownership deliberately.

Rebuild the application containers without deleting the Neo4j or Ollama data volumes:

```bash
docker compose up -d --build backend frontend
docker compose up -d neo4j ollama
docker compose ps
```

If you replace the whole Compose stack while it is currently stopped:

```bash
docker compose up -d --build
```

## Where logs are written

| Component | Readable local file | Live Docker command |
| --- | --- | --- |
| Frontend Nuxt server proxy | `logs/frontend/server.log` | `docker compose logs -f frontend` |
| Backend FastAPI / Neo4j queries / Ollama calls | `logs/backend/backend.log` | `docker compose logs -f backend` |
| Neo4j internal database logs | `logs/neo4j/` | `docker compose logs -f neo4j` |
| Ollama runtime | Docker-managed rotated log | `docker compose logs -f ollama` |
| Import and model initialization jobs | Docker-managed rotated log | `docker compose logs neo4j-import ollama-init` |

All container stdout/stderr logs use Docker's rotated `local` logging driver, capped at five 10 MB files per service.

To save a readable timestamped copy of the complete live service output:

```bash
./scripts/capture-logs.sh
```

## Diagnose an "Answer: Request could not be completed" failure

The UI now reports an HTTP status and, when available, a request ID. Use it to correlate the frontend proxy call and backend processing:

```bash
grep "REQUEST-ID-FROM-SCREEN" logs/frontend/server.log logs/backend/backend.log
```

Generate a compact report:

```bash
./scripts/diagnose.sh
```

Or inspect in real time while you reproduce the problem:

```bash
tail -f logs/frontend/server.log logs/backend/backend.log
```

In another terminal:

```bash
docker compose logs -f neo4j ollama
```

## Direct connectivity checks

```bash
curl -i http://localhost:8000/health
curl -i http://localhost:3000/api/examples
curl -i http://localhost:11434/api/tags

curl -i -X POST http://localhost:3000/api/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"Who owns system EMBARGO?"}'
```

Interpretation:

- `localhost:8000/health` fails: backend or Neo4j is not healthy; check `logs/backend/backend.log` and `logs/neo4j/`.
- Port `8000` works but `localhost:3000/api/examples` fails: frontend server proxy configuration or frontend container is failing; check `logs/frontend/server.log`.
- Graph API succeeds but shows `llm_status: "unavailable"`: Neo4j worked and the Ollama request failed; check `logs/backend/backend.log` and `docker compose logs ollama`.
- A response contains a request ID: search for it in both frontend and backend log files.
