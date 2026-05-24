from typing import Any


def _key(node_type: str, node_id: str | None, name: str) -> str:
    return f"{node_type}:{node_id or name}"


def build_graph(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Convert query evidence rows into v-network-graph nodes and edges.

    Nodes are keyed with type + stable identifier.  Display names are not used
    as database lookup IDs, which prevents node-detail 404 errors.
    """
    nodes: dict[str, dict[str, Any]] = {}
    edges: dict[str, dict[str, str]] = {}

    for index, row in enumerate(rows):
        source_name = row.get("source")
        target_name = row.get("target")
        if not source_name or not target_name:
            continue

        source_type = row.get("source_type", "Entity")
        target_type = row.get("target_type", "Entity")
        source_id = row.get("source_id") or source_name
        target_id = row.get("target_id") or target_name
        source_key = _key(source_type, source_id, source_name)
        target_key = _key(target_type, target_id, target_name)

        nodes[source_key] = {
            "id": source_id,
            "name": source_name,
            "type": source_type,
        }
        nodes[target_key] = {
            "id": target_id,
            "name": target_name,
            "type": target_type,
        }
        edges[f"e-{index}"] = {
            "source": source_key,
            "target": target_key,
            "label": row.get("relationship", "RELATED_TO"),
        }

    degrees = {node_key: 0 for node_key in nodes}
    for edge in edges.values():
        degrees[edge["source"]] += 1
        degrees[edge["target"]] += 1
    for node_key, node in nodes.items():
        node["degree"] = degrees[node_key]

    return {"nodes": nodes, "edges": edges}
