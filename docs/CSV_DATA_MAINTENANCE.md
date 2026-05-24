# Maintaining and scaling the CSV-backed Neo4j dataset

## Current loading model

The active importer uses Neo4j `MERGE` keyed by stable IDs, for example:

```cypher
MERGE (n:System {system_id: row.system_id})
SET n.name = row.name, ...
```

Treat IDs such as `S001`, `E005`, `T001` and `D001` as permanent identifiers.
Display names may change; IDs should not change just because a label shown in the GUI changes.

## Safe operations with the current importer

### Add a system

1. Add a new row to `data/neo4j_starter/import/systems_applications.csv` with a new `system_id`.
2. Add required relationship rows using that same ID, especially:
   - `team_owns_system.csv`
   - process/system usage files, when the system supports a process
   - pipeline/source-system relationship files, when it produces downstream data.
3. Run:

```bash
./scripts/import-and-verify.sh
```

### Rename a system

Edit only the `name` field in `systems_applications.csv` and keep the existing `system_id`.

Example:

```csv
S001,EMBARGO Screening Platform,...
```

Re-running the importer updates the existing `System` node rather than creating a second system.

### Change a system identifier

Avoid changing identifiers for a rename. Changing `S001` to `S099` is a migration, not a rename:
the importer will create `S099`; it will not remove `S001` automatically.

### Remove a system or move ownership

The current importer is deliberately additive/update-safe: it merges present CSV rows but does not remove nodes or old relationships that disappear from CSV. Therefore:

- Removing a CSV row does not delete the old Neo4j node.
- Moving ownership by replacing a row in `team_owns_system.csv` can leave the previous `OWNS_SYSTEM` relationship unless it is removed deliberately.

For local development, the cleanest destructive synchronization is a controlled clean database rebuild.
For production, use a reviewed migration query or add lifecycle fields such as `status=Retired` and validity dates before deleting historical governance evidence.

## Recommended scaling path

| Dataset change | Clean approach |
| --- | --- |
| New node or new relationship | Append CSV row(s), rerun importer, validate |
| Display-name/description change | Keep stable ID; update CSV field; rerun importer |
| ID correction | Reviewed migration; do not silently change the ID |
| Ownership reassignment | Migration that closes/removes old relationship and creates new relationship |
| Deletion | Soft-delete/retire in production; controlled full rebuild only for development |
| Large recurring loads | Move from hand-edited CSVs to versioned ingestion/reconciliation with import-run audit metadata |

## Validation after each load

Use the supplied helper:

```bash
./scripts/import-and-verify.sh
```

It re-runs the idempotent importer and reports:
- node counts by label;
- system ownership gaps;
- duplicate ownership candidates.
