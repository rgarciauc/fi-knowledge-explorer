# SUPER_BANK Knowledge Graph — single Docker stack

This version runs the active starter-compatible graph application through one root Docker Compose stack:

- Neo4j database and Browser
- automatic Neo4j seed import
- FastAPI backend
- Nuxt frontend
- Ollama local LLM service
- automatic Ollama model download

## Active graph dataset

Only this dataset is loaded:

```text
data/neo4j_starter/import/
data/neo4j_starter/cypher/import.cypher
```

Do not import `data/alternate_model_not_loaded/csv/` into this database because it uses a different label and relationship schema.

## Configure and run

```bash
cp .env.example .env
docker compose up --build -d
```

On the first run, Compose starts Neo4j and Ollama, imports the starter graph through the `neo4j-import` one-shot container, downloads the model through `ollama-init`, and only then starts the backend and frontend.

## Clean rebuild

Use this when deliberately resetting all local project data, including the Neo4j volume and Ollama model cache:

```bash
docker compose -f data/neo4j_starter/docker-compose.yml down -v --remove-orphans 2>/dev/null || true
docker compose down -v --remove-orphans 2>/dev/null || true
cp .env.example .env
docker compose up --build -d
```

The nested `data/neo4j_starter/docker-compose.yml` is legacy configuration from the earlier Neo4j-only starter stage. Do not use it to start the application after moving to this root stack.

## Service URLs

| Service | URL |
| --- | --- |
| Frontend | `http://localhost:3000` |
| FastAPI health | `http://localhost:8000/health` |
| Neo4j Browser | `http://localhost:7474` |
| Ollama models API | `http://localhost:11434/api/tags` |

Neo4j credentials use values in `.env`; the development default user is `neo4j` and default password is `SuperBank_ChangeMe_2026`.

## Verify the stack

```bash
./scripts/verify-stack.sh
```

Or test manually:

```bash
curl -fsS http://localhost:8000/health
curl -fsS http://localhost:11434/api/tags
curl -fsS -X POST http://localhost:8000/api/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"Who owns system EMBARGO?"}'
```

## Supported questions

```text
Who owns system EMBARGO?
Who is responsible for Sanctions Screening?
What is affected if system EMBARGO fails?
Show the pipeline for Payment Processing
What is the next step after Receive trigger/input - Payment Processing?
Show missing system owners
Show KPI summary
```

## Change the local LLM model

Change `.env`, for example:

```env
OLLAMA_MODEL=llama3.2:3b
LLM_ENABLED=true
```

Then pull the configured model and recreate services that use it:

```bash
docker compose up -d ollama
docker compose up --force-recreate ollama-init
docker compose up -d --build backend frontend
```

The backend sends only the query-result evidence rows to Ollama and falls back to a deterministic answer if the model service is unavailable.
