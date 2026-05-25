# SUPER_BANK Bank Operating Model v2

## Purpose

This model replaces the starter graph with a bank-operating and technology-governance graph designed to answer questions about:

- how payment instructions traverse IT Payments, Compliance, Settlement and final status update;
- which teams interact and depend on one another;
- which employee is the IT owner and business owner of a system;
- which controls are applied before payment release;
- how Input Hub provides external information to screening and surveillance systems;
- how Service Desk and Ticketing System support operational teams;
- how Identity Management governs access to systems;
- how EU Regulatory Office monitors DORA and GDPR oversight;
- which responsibilities are assigned to individual employees.

## Modeling choices

### Employee system ownership

A system has two accountability edges:

```text
(:Employee)-[:IT_OWNER_OF]->(:System)
(:Employee)-[:BUSINESS_OWNER_OF]->(:System)
```

A team may separately operate a system:

```text
(:Team)-[:MANAGES_SYSTEM]->(:System)
```

This distinction prevents “operates the platform” from being confused with personal accountability.

### Team interactions

Directed operational exchanges are modeled as:

```text
(:Team)-[:INTERACTS_WITH {interaction_type, description}]->(:Team)
```

Examples:

```text
IT Payments        -[SUBMITS_FOR_COMPLIANCE]-> IT Compliance
IT Compliance      -[RETURNS_GO_NO_GO]->        IT Payments
IT Payments        -[SENDS_FOR_SETTLEMENT]->    Settlement & Reconciliation
Settlement         -[RETURNS_SETTLEMENT_STATUS]-> IT Payments
```

### Payments are a process, not a single real transaction

The v2 seed models a canonical payment lifecycle. It does not store a real customer payment named `xxx`.

```text
(:BusinessProcess {name:'End-to-End Payment Execution'})
  -[:HAS_STEP]->(:ProcessStep)
```

This is appropriate for workflow and dependency questions. Adding real payment instances would require separate data-protection, retention and access controls and should not be done in a demo seed graph.

### Compliance decisions and controls

GO / NO-GO is represented as a decision step with an applied control:

```text
(:Control {name:'Sanctions and AML Screening Gate'})-[:APPLIES_TO]->
(:ProcessStep {name:'Compliance GO or NO-GO decision'})
```

### Input Hub data lineage

External data dependencies are represented with:

```text
(:ExternalSource)-[:FEEDS_SYSTEM]->(:System {name:'Input Hub System'})
(:System {name:'Sanctions Monitoring'})-[:DEPENDS_ON]->(:System {name:'Input Hub System'})
(:System {name:'Input Hub System'})-[:FEEDS_PIPELINE]->(:DataPipeline)-[:PRODUCES_DATASET]->(:Dataset)
```

### Regulatory frameworks

The model includes `RegulatoryFramework` nodes for DORA and GDPR and explicit links to systems. These nodes support graph exploration and oversight mapping; they are not a legal compliance determination.

## Migration strategy

The starter dataset and v2 dataset should not be co-imported into one development volume. Activate v2 with a clean Neo4j volume using:

```bash
./scripts/activate-bank-operating-model-v2.sh
```

After v2 is active:

- additions and property/name changes: edit v2 CSVs and run `./scripts/reimport-bank-operating-model-v2.sh`;
- deletions, ID replacements or relationship removals: use a reviewed migration or clean development reset;
- do not change stable identifiers merely to rename displayed entities.

## Questions supported by approved backend templates

```text
Show the end-to-end payment flow and GO or NO-GO decision.
How do the IT Payments and IT Compliance teams interact?
Who are the IT and business owners of Sanctions Monitoring?
Who works in the IT Compliance Department?
What systems depend on the Input Hub System?
How does the IT Service Desk support all teams?
Which systems are governed by Identity Management?
Which systems are under DORA oversight?
What responsibilities does Amira Haddad have?
What is affected if Sanctions Monitoring fails?.
```
