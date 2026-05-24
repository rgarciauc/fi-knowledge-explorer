# SUPER_BANK Bank Operating Model v2 — Question Pipeline

```text
Frontend question
  ↓
POST /api/ask
  ↓
Fast concept definitions when appropriate
  ↓
Entity catalogue + typo-tolerant matching
  ↓
Approved v2 intent route when known:
  - payment_flow
  - team_interactions
  - system_owners
  - department_employees
  - support_coverage
  - access_governance
  - regulatory_oversight
  - data_lineage
  - employee_responsibilities
  - system_impact
  - kpis
  ↓ otherwise
Ollama structured intent recognition
  ↓ if not covered
Broad graph retrieval
  ↓ only when still necessary
Validated read-only generated Cypher → EXPLAIN → timed execution
  ↓
Evidence graph + answer + query-trace badge in GUI
```

The active schema is `data/bank_operating_model_v2/`. The previous starter schema is deprecated for the v2 application.
