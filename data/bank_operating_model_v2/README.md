# Bank Operating Model v2 — Active Replacement Data Source

This versioned data source supersedes `data/neo4j_starter/` for the expanded banking knowledge graph.

## Why a new versioned folder

The previous starter graph was useful for early GUI and query work, but it does not represent:

- directed collaboration between IT Payments, IT Compliance and Settlement;
- compliance GO / NO-GO decisions in an end-to-end payment lifecycle;
- service desk support and ticketing usage across all teams;
- identity access governance across systems;
- dual employee-level IT owner and business owner accountability for systems;
- Input Hub data dependencies and external-source lineage;
- DORA / GDPR regulatory oversight;
- employee responsibilities and system controls.

Do not merge these CSVs into the old seed folder. Activate this model cleanly using the supplied migration script.

## New node labels

```text
Department
Team
Employee
System
ExternalSource
RegulatoryFramework
Control
Responsibility
BusinessProcess
ProcessStep
DataPipeline
Dataset
Project
```

## New core relationships

```text
(:Department)-[:HAS_TEAM]->(:Team)
(:Team)-[:HAS_EMPLOYEE]->(:Employee)
(:Employee)-[:LEADS_TEAM]->(:Team)
(:Employee)-[:RESPONSIBLE_FOR]->(:Responsibility)

(:Team)-[:MANAGES_SYSTEM]->(:System)
(:Employee)-[:IT_OWNER_OF]->(:System)
(:Employee)-[:BUSINESS_OWNER_OF]->(:System)
(:Team)-[:INTERACTS_WITH {interaction_type, description}]->(:Team)
(:Team)-[:SUPPORTS_TEAM]->(:Team)
(:Team)-[:USES_SYSTEM]->(:System)
(:Team)-[:GOVERNS_ACCESS_TO]->(:System)

(:BusinessProcess)-[:HAS_STEP]->(:ProcessStep)
(:Team)-[:PERFORMS_STEP]->(:ProcessStep)
(:ProcessStep)-[:USES_SYSTEM]->(:System)
(:Control)-[:APPLIES_TO]->(:ProcessStep)
(:Control)-[:IMPLEMENTED_BY]->(:System)

(:ExternalSource)-[:FEEDS_SYSTEM]->(:System)
(:System)-[:DEPENDS_ON]->(:System)
(:System)-[:FEEDS_PIPELINE]->(:DataPipeline)
(:DataPipeline)-[:PRODUCES_DATASET]->(:Dataset)
(:Dataset)-[:USED_BY_SYSTEM]->(:System)
(:Dataset)-[:USED_BY_PROCESS]->(:BusinessProcess)

(:Team)-[:MONITORS_FRAMEWORK]->(:RegulatoryFramework)
(:RegulatoryFramework)-[:APPLIES_TO]->(:System)
```

## Modeled payment lifecycle

```text
IT Payments
  → Submit for compliance screening
IT Compliance / Compliance Decision
  → Screen sanctions, AML, restricted parties and unusual-risk alerts
  → Return GO or NO-GO
IT Payments
  → Release approved payment via SEPA or SWIFT
Settlement & Reconciliation
  → Confirm settlement and reconcile records
IT Payments / Payment Processing Core
  → Automatic final status update
```

## Data maintenance rules

- Keep IDs stable; change visible names and descriptions without changing IDs.
- Add new nodes and relationships with new IDs and rerun the importer.
- Treat removal or ID replacement as an explicit migration.
- For a clean development switch from the starter model to v2, reset only the Neo4j volume and import v2.
