"""PulseStack AI — Dashboard Overview API."""

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.api.v1.incidents import _get_user_org_id
from app.core.config import get_settings
from app.core.database import get_db
from app.core.elasticsearch import get_es
from app.models.models import Alert, Incident, Service, User
from app.schemas.schemas import DashboardOverview

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
settings = get_settings()


@router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    es=Depends(get_es),
):
    """Aggregate dashboard metrics for the overview page."""
    org_id = await _get_user_org_id(user, db)
    now = datetime.now(timezone.utc)
    last_24h = now - timedelta(hours=24)

    # Service counts
    svc_result = await db.execute(select(Service).where(Service.org_id == org_id))
    services = svc_result.scalars().all()
    total_services = len(services)
    healthy_services = sum(1 for s in services if s.status == "healthy")
    degraded_services = total_services - healthy_services

    # Incident counts
    open_result = await db.execute(
        select(func.count()).select_from(Incident).where(
            Incident.org_id == org_id,
            Incident.status.in_(["open", "investigating"]),
        )
    )
    open_incidents = open_result.scalar() or 0

    critical_result = await db.execute(
        select(func.count()).select_from(Incident).where(
            Incident.org_id == org_id,
            Incident.severity == "critical",
            Incident.status != "resolved",
        )
    )
    critical_incidents = critical_result.scalar() or 0

    # Active alerts
    alert_result = await db.execute(
        select(func.count()).select_from(Alert).where(
            Alert.org_id == org_id,
            Alert.status == "firing",
        )
    )
    active_alerts = alert_result.scalar() or 0

    # Logs ingested in last 24h (from ES)
    try:
        count_result = await es.count(
            index=settings.ES_LOG_INDEX,
            query={"range": {"timestamp": {"gte": last_24h.isoformat()}}},
        )
        logs_ingested_24h = count_result["count"]
    except Exception:
        logs_ingested_24h = 0

    # Recent incidents
    recent_inc_result = await db.execute(
        select(Incident)
        .where(Incident.org_id == org_id)
        .order_by(Incident.created_at.desc())
        .limit(5)
    )
    recent_incidents = recent_inc_result.scalars().all()

    # Recent alerts
    recent_alert_result = await db.execute(
        select(Alert)
        .where(Alert.org_id == org_id)
        .order_by(Alert.fired_at.desc())
        .limit(5)
    )
    recent_alerts = recent_alert_result.scalars().all()

    return DashboardOverview(
        total_services=total_services,
        healthy_services=healthy_services,
        degraded_services=degraded_services,
        open_incidents=open_incidents,
        critical_incidents=critical_incidents,
        active_alerts=active_alerts,
        logs_ingested_24h=logs_ingested_24h,
        ai_sessions_24h=0,
        recent_incidents=recent_incidents,
        recent_alerts=recent_alerts,
    )
