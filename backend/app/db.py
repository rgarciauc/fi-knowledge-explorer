from typing import Any

from neo4j import GraphDatabase

from .config import settings
from .graph_schema import NODE_KEYS


driver = GraphDatabase.driver(
    settings.neo4j_uri,
    auth=(settings.neo4j_user, settings.neo4j_password),
)


def close_driver() -> None:
    driver.close()


def verify_connectivity() -> None:
    driver.verify_connectivity()


def read(query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    with driver.session() as session:
        return [record.data() for record in session.run(query, params or {})]


def node_details(label: str, node_id: str) -> dict[str, Any] | None:
    """Read one stored graph node using a whitelisted label and stable identifier."""
    key = NODE_KEYS.get(label)
    if not key:
        return None

    query = f"""
    MATCH (n:{label} {{{key}: $node_id}})
    OPTIONAL MATCH (n)-[r]-(m)
    RETURN labels(n) AS labels,
           properties(n) AS properties,
           [item IN collect(
             CASE WHEN r IS NULL THEN NULL ELSE {{
               relationship: type(r),
               connected_labels: labels(m),
               connected_properties: properties(m)
             }} END
           ) WHERE item IS NOT NULL] AS relationships
    LIMIT 1
    """
    rows = read(query, {"node_id": node_id})
    return rows[0] if rows else None
