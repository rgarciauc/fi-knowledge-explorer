import logging
from typing import Any

from neo4j import GraphDatabase

from .config import settings
from .graph_schema import NODE_KEYS


logger = logging.getLogger("super_bank.neo4j")

driver = GraphDatabase.driver(
    settings.neo4j_uri,
    auth=(settings.neo4j_user, settings.neo4j_password),
)


def close_driver() -> None:
    logger.info("neo4j.driver_closing")
    driver.close()


def verify_connectivity() -> None:
    try:
        driver.verify_connectivity()
        logger.debug("neo4j.connectivity_ok uri=%s", settings.neo4j_uri)
    except Exception:
        logger.exception("neo4j.connectivity_failed uri=%s", settings.neo4j_uri)
        raise


def _query_name(query: str) -> str:
    compact = " ".join(query.split())
    return compact[:100]


def read(query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    parameters = params or {}
    try:
        with driver.session() as session:
            rows = [record.data() for record in session.run(query, parameters)]
        logger.info(
            "neo4j.query_ok query=%r params=%r rows=%d",
            _query_name(query),
            parameters,
            len(rows),
        )
        return rows
    except Exception:
        logger.exception(
            "neo4j.query_failed query=%r params=%r",
            _query_name(query),
            parameters,
        )
        raise


def node_details(label: str, node_id: str) -> dict[str, Any] | None:
    """Read one stored graph node using a whitelisted label and stable identifier."""
    key = NODE_KEYS.get(label)
    if not key:
        logger.warning("neo4j.node_details_unsupported_label label=%s node_id=%s", label, node_id)
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
