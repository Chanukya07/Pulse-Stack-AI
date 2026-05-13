"""PulseStack AI — Log Ingestion & Search API Routes."""

from datetime import datetime, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps import get_current_user
from app.core.config import get_settings
from app.core.elasticsearch import get_es
from app.models.models import User
from app.schemas.schemas import LogBatchIngest, LogSearchResponse

router = APIRouter(prefix="/logs", tags=["Logs"])
settings = get_settings()


@router.post("/ingest", status_code=202)
async def ingest_logs(
    payload: LogBatchIngest,
    user: Annotated[User, Depends(get_current_user)],
    es=Depends(get_es),
):
    """Ingest a batch of log entries into Elasticsearch."""
    operations: list[dict[str, Any]] = []
    for log in payload.logs:
        doc = log.model_dump()
        if doc["timestamp"] is None:
            doc["timestamp"] = datetime.now(timezone.utc).isoformat()
        else:
            doc["timestamp"] = doc["timestamp"].isoformat()

        # Add org context
        doc["org_id"] = str(user.org_memberships[0].org_id) if user.org_memberships else "default"

        operations.append({"index": {"_index": settings.ES_LOG_INDEX}})
        operations.append(doc)

    if operations:
        await es.bulk(operations=operations, refresh="wait_for")

    return {"accepted": len(payload.logs), "index": settings.ES_LOG_INDEX}


@router.get("/search", response_model=LogSearchResponse)
async def search_logs(
    user: Annotated[User, Depends(get_current_user)],
    es=Depends(get_es),
    q: str | None = Query(None, description="Full-text search query"),
    service: str | None = Query(None),
    level: str | None = Query(None),
    start_time: datetime | None = Query(None),
    end_time: datetime | None = Query(None),
    size: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """Search logs in Elasticsearch with filters."""
    must_clauses: list[dict] = []
    filter_clauses: list[dict] = []

    if q:
        must_clauses.append({"match": {"message": q}})

    if service:
        filter_clauses.append({"term": {"service": service}})

    if level:
        filter_clauses.append({"term": {"level": level}})

    if start_time or end_time:
        range_query: dict[str, Any] = {}
        if start_time:
            range_query["gte"] = start_time.isoformat()
        if end_time:
            range_query["lte"] = end_time.isoformat()
        filter_clauses.append({"range": {"timestamp": range_query}})

    query = {
        "bool": {
            "must": must_clauses or [{"match_all": {}}],
            "filter": filter_clauses,
        }
    }

    result = await es.search(
        index=settings.ES_LOG_INDEX,
        query=query,
        from_=offset,
        size=size,
        sort=[{"timestamp": {"order": "desc"}}],
    )

    hits = result["hits"]
    logs = [
        {**hit["_source"], "_id": hit["_id"]}
        for hit in hits["hits"]
    ]

    return LogSearchResponse(
        total=hits["total"]["value"],
        logs=logs,
        took_ms=result["took"],
    )
