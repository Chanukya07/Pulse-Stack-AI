"""PulseStack AI — Pydantic Request/Response Schemas."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


# ── Auth ────────────────────────────────────────────────────
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str | None
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Organization ────────────────────────────────────────────
class OrgCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")


class OrgResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    plan: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Service ─────────────────────────────────────────────────
class ServiceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    service_type: str | None = None
    environment: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ServiceUpdate(BaseModel):
    name: str | None = None
    status: str | None = None
    service_type: str | None = None
    environment: str | None = None
    metadata: dict[str, Any] | None = None


class ServiceResponse(BaseModel):
    id: uuid.UUID
    org_id: uuid.UUID
    name: str
    service_type: str | None
    environment: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Log Ingestion ───────────────────────────────────────────
class LogEntry(BaseModel):
    timestamp: datetime | None = None
    service: str
    level: str = "info"
    message: str
    source: str | None = None
    host: str | None = None
    environment: str | None = None
    trace_id: str | None = None
    span_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class LogBatchIngest(BaseModel):
    logs: list[LogEntry] = Field(min_length=1, max_length=1000)


class LogSearchParams(BaseModel):
    query: str | None = None
    service: str | None = None
    level: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    size: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


class LogSearchResponse(BaseModel):
    total: int
    logs: list[dict[str, Any]]
    took_ms: int


# ── Incident ────────────────────────────────────────────────
class IncidentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: str | None = None
    severity: str = Field(pattern=r"^(critical|high|medium|low)$")
    source: str | None = None
    service_ids: list[uuid.UUID] = Field(default_factory=list)


class IncidentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    severity: str | None = None
    status: str | None = None
    assigned_to: uuid.UUID | None = None


class IncidentResponse(BaseModel):
    id: uuid.UUID
    org_id: uuid.UUID
    title: str
    description: str | None
    severity: str
    status: str
    source: str | None
    ai_summary: str | None
    ai_root_cause: str | None
    ai_confidence: float | None
    assigned_to: uuid.UUID | None
    resolved_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Alert ───────────────────────────────────────────────────
class AlertRuleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    condition: dict[str, Any]
    severity: str = "medium"
    channels: list[dict[str, Any]] = Field(default_factory=list)


class AlertRuleResponse(BaseModel):
    id: uuid.UUID
    org_id: uuid.UUID
    name: str
    condition: dict[str, Any]
    severity: str
    channels: list[dict[str, Any]]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertResponse(BaseModel):
    id: uuid.UUID
    org_id: uuid.UUID
    service_id: uuid.UUID | None
    incident_id: uuid.UUID | None
    rule_name: str
    severity: str
    status: str
    message: str | None
    fired_at: datetime
    resolved_at: datetime | None

    model_config = {"from_attributes": True}


# ── Dashboard ───────────────────────────────────────────────
class DashboardOverview(BaseModel):
    total_services: int
    healthy_services: int
    degraded_services: int
    open_incidents: int
    critical_incidents: int
    active_alerts: int
    logs_ingested_24h: int
    ai_sessions_24h: int
    recent_incidents: list[IncidentResponse]
    recent_alerts: list[AlertResponse]


# ── Pagination ──────────────────────────────────────────────
class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
