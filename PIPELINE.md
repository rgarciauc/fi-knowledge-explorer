HIGHT-LEVEL
Frontend question
   ↓
POST /api/ask
   ↓
classify_question(question)
   ↓
Select one predefined Cypher query template
   ↓
Extract a search term such as "EMBARGO"
   ↓
Execute fixed query against Neo4j
   ↓
Optionally send returned rows to Ollama to generate an explanation

INTENT-DETECTION:
Fast known intent → approved query template
        ↓ no good match
LLM structured intent recognition → approved query template
        ↓ not solvable by templates
Broad evidence retrieval → answer if enough evidence exists
        ↓ still insufficient
LLM-generated read-only Cypher → validate → EXPLAIN → execute with limit
        ↓ ambiguous / unsupported
Clarifying answer with useful discovered entities