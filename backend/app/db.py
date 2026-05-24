import logging
from collections.abc import Mapping
from typing import Any

from neo4j import GraphDatabase, Query, READ_ACCESS
from neo4j.time import Date, DateTime, Duration, Time

from .config import settings
from .graph_schema import NODE_KEYS


logger = logging.getLogger("super_bank.neo4j")

driver = GraphDatabase.driver(
    settings.neo4j_uri,
    auth=(settings.neo4j_user, settings.neo4j_password),
)


def _json_safe(value: Any) -> Any:
    """Convert Neo4j temporal/container values into JSON-serializable API values."""
    if isinstance(value, (Date, DateTime, Duration, Time)):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    return value


def _records_to_data(result: Any) -> list[dict[str, Any]]:
    return [_json_safe(record.data()) for record in result]


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
    return " ".join(query.split())[:130]


def read(query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    parameters = params or {}
    try:
        with driver.session(default_access_mode=READ_ACCESS) as session:
            rows = _records_to_data(session.run(query, parameters))
        logger.info("neo4j.query_ok query=%r params=%r rows=%d", _query_name(query), parameters, len(rows))
        return rows
    except Exception:
        logger.exception("neo4j.query_failed query=%r params=%r", _query_name(query), parameters)
        raise


def read_with_timeout(
    query: str,
    params: dict[str, Any] | None = None,
    *,
    timeout_seconds: float,
    metadata: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    parameters = params or {}
    configured_query = Query(query, timeout=timeout_seconds, metadata=metadata or {})
    try:
        with driver.session(default_access_mode=READ_ACCESS) as session:
            rows = _records_to_data(session.run(configured_query, parameters))
        logger.info(
            "neo4j.generated_query_ok query=%r rows=%d timeout_seconds=%.1f",
            _query_name(query),
            len(rows),
            timeout_seconds,
        )
        return rows
    except Exception:
        logger.exception("neo4j.generated_query_failed query=%r params=%r", _query_name(query), parameters)
        raise


def explain_read_query(
    query: str,
    params: dict[str, Any] | None = None,
    *,
    timeout_seconds: float,
    metadata: dict[str, Any] | None = None,
) -> None:
    parameters = params or {}
    planned = Query(f"EXPLAIN {query}", timeout=timeout_seconds, metadata=metadata or {})
    try:
        with driver.session(default_access_mode=READ_ACCESS) as session:
            session.run(planned, parameters).consume()
        logger.info("neo4j.generated_query_explain_ok query=%r", _query_name(query))
    except Exception:
        logger.exception("neo4j.generated_query_explain_failed query=%r", _query_name(query))
        raise


def node_details(label: str, node_id: str) -> dict[str, Any] | None:
    """Read one stored graph node by stable ID, with a safe exact-name fallback.

    Approved templates return stable IDs. Broad or generated read evidence can
    still contain the visible node name in source_id/target_id. In that case,
    clicking the already displayed node should resolve the stored node by its
    exact name rather than returning a misleading 404.
    """
    key = NODE_KEYS.get(label)
    if not key:
        logger.warning("neo4j.node_details_unsupported_label label=%s node_ref=%s", label, node_id)
        return None

    query = f"""
    MATCH (n:{label})
    WHERE n.{key} = $node_ref
       OR toLower(coalesce(n.name, '')) = toLower($node_ref)
    WITH n,
         CASE WHEN n.{key} = $node_ref THEN 0 ELSE 1 END AS match_rank,
         CASE WHEN n.{key} = $node_ref THEN 'stable_id' ELSE 'exact_name_fallback' END AS matched_by
    ORDER BY match_rank
    LIMIT 1
    OPTIONAL MATCH (n)-[r]-(m)
    WITH n, matched_by, [item IN collect(
        CASE WHEN r IS NULL THEN NULL ELSE {{
          relationship: type(r),
          connected_labels: labels(m),
          connected_properties: properties(m)
        }} END
    ) WHERE item IS NOT NULL] AS relationships
    RETURN labels(n) AS labels,
           n.{key} AS stable_id,
           matched_by,
           properties(n) AS properties,
           relationships
    LIMIT 1
    """
    try:
        rows = read(query, {"node_ref": node_id})
        if rows:
            logger.info(
                "neo4j.node_details_ok label=%s node_ref=%s stable_id=%s matched_by=%s",
                label,
                node_id,
                rows[0].get("stable_id"),
                rows[0].get("matched_by"),
            )
            return rows[0]
        logger.warning("neo4j.node_details_not_found label=%s node_ref=%s", label, node_id)
        return None
    except Exception:
        logger.exception("neo4j.node_details_failed label=%s node_ref=%s", label, node_id)
        raise
