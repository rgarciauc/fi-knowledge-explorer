# SUPER_BANK — Start Here

This folder is the first runnable stage of the SUPER_BANK transparency graph.
It starts only Neo4j and loads the supplied synthetic CSV dataset. Build FastAPI and Vue after this database step is working.

## Contents
- `docker-compose.yml`: runs one local Neo4j Community container.
- `import/`: all supplied node and relationship CSVs.
- `cypher/import.cypher`: creates constraints, imports nodes, and connects relationships.
- `cypher/sample_queries.cypher`: test and visualization queries.

## Credentials for the starter configuration
- User: `neo4j`
- Password: `SuperBank_ChangeMe_2026`

Change the password in `docker-compose.yml` before publishing or sharing the project.

## Run on macOS/Linux
```bash
cd SUPER_BANK_STARTER
docker compose up -d
docker compose ps
# Once Neo4j is healthy/running, import:
docker exec -i super_bank_neo4j cypher-shell -u neo4j -p SuperBank_ChangeMe_2026 < cypher/import.cypher
```

## Run import on Windows PowerShell
```powershell
cd SUPER_BANK_STARTER
docker compose up -d
docker compose ps
Get-Content .\cypher\import.cypher | docker exec -i super_bank_neo4j cypher-shell -u neo4j -p SuperBank_ChangeMe_2026
```

## Open Neo4j
Open `http://localhost:7474` in your browser and log in using the credentials above.

## Stop/start later
```bash
docker compose stop
docker compose start
```

## Remove the database and start over
Warning: this deletes all imported graph data.
```bash
docker compose down -v
```
Then run the startup and import commands again.
