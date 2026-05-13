"""PulseStack AI — Incident Management API Routes."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.deps import get_current_user, require_editor
from app.core.database import get_db
from app.models.models import Incident, IncidentService, OrgMember, User
from app.schemas.schemas import IncidentCreate, IncidentResponse, IncidentUpdate

router = APIRouter(prefix="/incidents", tags=["Incidents"])


async def _get_user_org_id(user: User, db: AsyncSession) -> uuid.UUID:
    """Get the primary org ID for a user."""
    result = await db.execute(select(OrgMember.org_id).where(OrgMember.user_id == user.id).limit(1))
    org_id = result.scalar_one_or_none()
    if not org_id:
        raise HTTPException(status_code=400, detail="User has no organization")
    return org_id


@router.get("", response_model=list[IncidentResponse])
async def list_incidents(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    severity: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List incidents for the user's organization."""
    org_id = await _get_user_org_id(user, db)
    query = select(Incident).where(Incident.org_id == org_id)

    if severity:
        query = query.where(Incident.severity == severity)
    if status_filter:
        query = query.where(Incident.status == status_filter)

    query = query.order_by(Incident.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    payload: IncidentCreate,
    user: Annotated[User, Depends(require_editor)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new incident."""
    org_id = await _get_user_org_id(user, db)

    incident = Incident(
        org_id=org_id,
        title=payload.title,
        description=payload.description,
        severity=payload.severity,
        source=payload.source,
    )
    db.add(incident)
    await db.flush()

    # Link affected services
    for svc_id in payload.service_ids:
        db.add(IncidentService(incident_id=incident.id, service_id=svc_id))

    return incident


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a single incident by ID."""
    org_id = await _get_user_org_id(user, db)
    result = await db.execute(
        select(Incident).where(Incident.id == incident_id, Incident.org_id == org_id)
    )
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: uuid.UUID,
    payload: IncidentUpdate,
    user: Annotated[User, Depends(require_editor)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update an incident."""
    org_id = await _get_user_org_id(user, db)
    result = await db.execute(
        select(Incident).where(Incident.id == incident_id, Incident.org_id == org_id)
    )
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(incident, field, value)

    return incident
