"""PulseStack AI — Service Registry API Routes."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, require_editor
from app.api.v1.incidents import _get_user_org_id
from app.core.database import get_db
from app.models.models import Service, User
from app.schemas.schemas import ServiceCreate, ServiceResponse, ServiceUpdate

router = APIRouter(prefix="/services", tags=["Services"])


@router.get("", response_model=list[ServiceResponse])
async def list_services(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    environment: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
):
    """List monitored services for the user's organization."""
    org_id = await _get_user_org_id(user, db)
    query = select(Service).where(Service.org_id == org_id)
    if environment:
        query = query.where(Service.environment == environment)
    if status_filter:
        query = query.where(Service.status == status_filter)
    query = query.order_by(Service.name)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_service(
    payload: ServiceCreate,
    user: Annotated[User, Depends(require_editor)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Register a new service to monitor."""
    org_id = await _get_user_org_id(user, db)
    service = Service(
        org_id=org_id,
        name=payload.name,
        service_type=payload.service_type,
        environment=payload.environment,
        metadata_=payload.metadata,
    )
    db.add(service)
    return service


@router.patch("/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: uuid.UUID,
    payload: ServiceUpdate,
    user: Annotated[User, Depends(require_editor)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update a monitored service."""
    org_id = await _get_user_org_id(user, db)
    result = await db.execute(
        select(Service).where(Service.id == service_id, Service.org_id == org_id)
    )
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "metadata" in update_data:
        update_data["metadata_"] = update_data.pop("metadata")
    for field, value in update_data.items():
        setattr(service, field, value)

    return service


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: uuid.UUID,
    user: Annotated[User, Depends(require_editor)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Remove a monitored service."""
    org_id = await _get_user_org_id(user, db)
    result = await db.execute(
        select(Service).where(Service.id == service_id, Service.org_id == org_id)
    )
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    await db.delete(service)
