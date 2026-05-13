"""PulseStack AI — Investigation Agent Tools.

Each tool is an async function that gathers data from the platform's
data stores (Elasticsearch, PostgreSQL) and returns structured context
for the agent to reason over.

Tools degrade gracefully — if a data source is unavailable they return
empty results so the agent can still produce a best-effort analysis.
"""

from __future__ import annotations

import traceback
from typing import Any

from app.core.config import get_settings
from app.services.ai_service import cluster_logs

settings = get_settings()


# ── Tool: Fetch Logs from Elasticsearch ─────────────────────


async def fetch_logs_tool(
    query: str = "",
    service: str | None = None,
    level: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """Search Elasticsearch for logs matching filters.

    Returns a list of log dicts, or an empty list if ES is unavailable.
    """
    try:
        from app.core.elasticsearch import get_es_client

        es = get_es_client()

        must_clauses: list[dict] = []
        filter_clauses: list[dict] = []

        if query:
            must_clauses.append({"match": {"message": query}})
        if service:
            filter_clauses.append({"term": {"service": service}})
        if level:
            filter_clauses.append({"term": {"level": level}})

        es_query = {
            "bool": {
                "must": must_clauses or [{"match_all": {}}],
                "filter": filter_clauses,
            }
        }

        result = await es.search(
            index=settings.ES_LOG_INDEX,
            query=es_query,
            size=limit,
            sort=[{"timestamp": {"order": "desc"}}],
        )

        return [
            {**hit["_source"], "_id": hit["_id"]}
            for hit in result["hits"]["hits"]
        ]

    except Exception as e:
        # Fallback for Windows local development without Docker/Elasticsearch
        try:
            import json
            import os
            
            logs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'local_logs.json')
            if not os.path.exists(logs_path):
                return []
                
            with open(logs_path, 'r', encoding='utf-8') as f:
                logs = [json.loads(line) for line in f if line.strip()]
                
            # Basic manual filtering
            filtered = []
            for log in reversed(logs): # Newest first
                if service and log.get("service") != service:
                    continue
                if level and log.get("level") != level:
                    continue
                if query and query.lower() not in log.get("message", "").lower():
                    continue
                filtered.append(log)
                if len(filtered) >= limit:
                    break
                    
            return filtered
        except Exception as fallback_e:
            print(f"[Agent Tool] fetch_logs_tool fallback failed: {fallback_e}")
            return []


# ── Tool: Cluster Logs ──────────────────────────────────────


async def cluster_logs_tool(
    logs: list[dict[str, Any]],
    n_clusters: int = 5,
) -> dict[str, Any]:
    """Cluster log messages using TF-IDF + KMeans (local, no LLM call).

    Returns cluster summary dict, or empty clusters on failure.
    """
    try:
        if not logs:
            return {"clusters": [], "note": "No logs provided for clustering"}
        return await cluster_logs(logs, n_clusters=n_clusters)
    except Exception as e:
        print(f"[Agent Tool] cluster_logs_tool failed: {e}")
        return {"clusters": [], "error": str(e)}


# ── Tool: Query Incident from Database ──────────────────────


async def fetch_incident_tool(incident_id: str) -> dict[str, Any]:
    """Load incident details from PostgreSQL by ID.

    Returns incident dict, or empty dict if DB is unavailable.
    """
    try:
        from sqlalchemy import select
        from app.core.database import _create_session_factory
        from app.models.models import Incident

        session_factory = _create_session_factory()
        async with session_factory() as session:
            result = await session.execute(
                select(Incident).where(Incident.id == incident_id)
            )
            incident = result.scalar_one_or_none()

            if not incident:
                return {"error": f"Incident {incident_id} not found"}

            return {
                "id": str(incident.id),
                "title": incident.title,
                "description": incident.description or "",
                "severity": incident.severity,
                "status": incident.status,
                "source": incident.source or "",
                "ai_summary": incident.ai_summary or "",
                "ai_root_cause": incident.ai_root_cause or "",
                "created_at": incident.created_at.isoformat() if incident.created_at else "",
                "resolved_at": incident.resolved_at.isoformat() if incident.resolved_at else "",
            }

    except Exception as e:
        print(f"[Agent Tool] fetch_incident_tool failed: {e}")
        return {"error": str(e)}


# ── Tool: List Services ─────────────────────────────────────


async def list_services_tool() -> list[dict[str, Any]]:
    """List all registered services from PostgreSQL.

    Returns service list, or empty list if DB is unavailable.
    """
    try:
        from sqlalchemy import select
        from app.core.database import _create_session_factory
        from app.models.models import Service

        session_factory = _create_session_factory()
        async with session_factory() as session:
            result = await session.execute(select(Service))
            services = result.scalars().all()

            return [
                {
                    "id": str(s.id),
                    "name": s.name,
                    "service_type": s.service_type or "",
                    "environment": s.environment or "",
                    "status": s.status,
                }
                for s in services
            ]

    except Exception as e:
        print(f"[Agent Tool] list_services_tool failed: {e}")
        return []


# ── Tool: Update Incident with AI Findings ──────────────────


async def update_incident_ai_fields(
    incident_id: str,
    summary: str,
    root_cause: str,
    confidence: float,
) -> dict[str, Any]:
    """Write AI analysis results back into the Incident record.

    Returns success/failure dict.
    """
    try:
        from sqlalchemy import select
        from app.core.database import _create_session_factory
        from app.models.models import Incident

        session_factory = _create_session_factory()
        async with session_factory() as session:
            result = await session.execute(
                select(Incident).where(Incident.id == incident_id)
            )
            incident = result.scalar_one_or_none()

            if not incident:
                return {"success": False, "error": f"Incident {incident_id} not found"}

            incident.ai_summary = summary
            incident.ai_root_cause = root_cause
            incident.ai_confidence = confidence

            await session.commit()
            return {"success": True, "incident_id": incident_id}

    except Exception as e:
        print(f"[Agent Tool] update_incident_ai_fields failed: {e}")
        return {"success": False, "error": str(e)}
