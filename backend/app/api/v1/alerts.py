"""PulseStack AI — Alerts API Routes."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, require_editor
from app.api.v1.incidents import _get_user_org_id
from app.core.database import get_db
from app.models.models import Alert, AlertRule, User
from app.schemas.schemas import AlertResponse, AlertRuleCreate, AlertRuleResponse

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=list[AlertResponse])
async def list_alerts(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    severity: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List alerts for the user's organization."""
    org_id = await _get_user_org_id(user, db)
    query = select(Alert).where(Alert.org_id == org_id)

    if severity:
        query = query.where(Alert.severity == severity)
    if status_filter:
        query = query.where(Alert.status == status_filter)

    query = query.order_by(Alert.fired_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/rules", response_model=list[AlertRuleResponse])
async def list_alert_rules(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List alert rules for the user's organization."""
    org_id = await _get_user_org_id(user, db)
    result = await db.execute(
        select(AlertRule).where(AlertRule.org_id == org_id).order_by(AlertRule.created_at.desc())
    )
    return result.scalars().all()


@router.post("/rules", response_model=AlertRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_alert_rule(
    payload: AlertRuleCreate,
    user: Annotated[User, Depends(require_editor)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new alert rule."""
    org_id = await _get_user_org_id(user, db)
    rule = AlertRule(
        org_id=org_id,
        name=payload.name,
        condition=payload.condition,
        severity=payload.severity,
        channels=payload.channels,
    )
    db.add(rule)
    return rule
