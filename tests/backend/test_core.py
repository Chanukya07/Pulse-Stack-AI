"""PulseStack AI — Backend Unit & Integration Tests."""

import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

# Check if asyncpg is available (it requires C compilation, unavailable on Windows without build tools)
try:
    import asyncpg  # noqa: F401
    HAS_ASYNCPG = True
except ImportError:
    HAS_ASYNCPG = False

needs_db = pytest.mark.skipif(not HAS_ASYNCPG, reason="asyncpg not available (requires C compiler)")

# ── Unit Tests: Security Module ─────────────────────────────


class TestSecurity:
    """Test JWT and password utilities."""

    def test_password_hashing(self):
        from app.core.security import hash_password, verify_password

        password = "SecureP@ssw0rd!"
        hashed = hash_password(password)

        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False

    def test_password_hash_is_unique(self):
        from app.core.security import hash_password

        h1 = hash_password("same_password")
        h2 = hash_password("same_password")
        assert h1 != h2  # bcrypt uses random salt

    def test_create_access_token(self):
        from app.core.security import create_access_token, decode_token

        data = {"sub": "user-123", "email": "test@example.com", "role": "admin"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

        # Decode should return valid payload
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "user-123"
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "admin"
        assert payload["type"] == "access"

    def test_create_refresh_token(self):
        from app.core.security import create_refresh_token, decode_token

        data = {"sub": "user-456"}
        token = create_refresh_token(data)

        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "user-456"
        assert payload["type"] == "refresh"

    def test_decode_invalid_token(self):
        from app.core.security import decode_token

        result = decode_token("invalid.token.here")
        assert result is None

    def test_decode_empty_token(self):
        from app.core.security import decode_token

        result = decode_token("")
        assert result is None

    def test_token_contains_expiry(self):
        from app.core.security import create_access_token, decode_token

        token = create_access_token({"sub": "test"})
        payload = decode_token(token)
        assert "exp" in payload


# ── Unit Tests: Config Module ───────────────────────────────


class TestConfig:
    """Test application configuration."""

    def test_settings_load(self):
        from app.core.config import get_settings

        settings = get_settings()
        assert settings.APP_NAME == "PulseStack AI"
        assert settings.API_V1_PREFIX == "/api/v1"

    def test_settings_defaults(self):
        from app.core.config import get_settings

        settings = get_settings()
        assert settings.ENVIRONMENT == "development"
        assert settings.DEBUG is True
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
        assert settings.REFRESH_TOKEN_EXPIRE_DAYS == 7

    def test_settings_cached(self):
        from app.core.config import get_settings

        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2  # Should be the same cached instance

    def test_is_production(self):
        from app.core.config import get_settings

        settings = get_settings()
        assert settings.is_production is False


# ── Unit Tests: Pydantic Schemas ────────────────────────────


class TestSchemas:
    """Test Pydantic request/response schema validation."""

    def test_user_register_valid(self):
        from app.schemas.schemas import UserRegister

        user = UserRegister(
            email="test@example.com",
            password="securepass123",
            full_name="Test User",
        )
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"

    def test_user_register_invalid_email(self):
        from app.schemas.schemas import UserRegister
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            UserRegister(email="not-an-email", password="securepass", full_name="Test")

    def test_user_register_password_too_short(self):
        from app.schemas.schemas import UserRegister
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            UserRegister(email="test@example.com", password="short", full_name="Test")

    def test_log_entry_defaults(self):
        from app.schemas.schemas import LogEntry

        log = LogEntry(service="api-gateway", message="Request processed")
        assert log.level == "info"
        assert log.timestamp is None
        assert log.metadata == {}

    def test_log_entry_full(self):
        from app.schemas.schemas import LogEntry

        log = LogEntry(
            service="payment-api",
            level="error",
            message="Connection timeout",
            host="node-1",
            trace_id="trace-abc",
            metadata={"duration_ms": 3000},
        )
        assert log.level == "error"
        assert log.host == "node-1"
        assert log.metadata["duration_ms"] == 3000

    def test_log_batch_ingest_min_length(self):
        from app.schemas.schemas import LogBatchIngest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            LogBatchIngest(logs=[])

    def test_log_batch_ingest_valid(self):
        from app.schemas.schemas import LogBatchIngest, LogEntry

        batch = LogBatchIngest(
            logs=[LogEntry(service="test", message="hello")]
        )
        assert len(batch.logs) == 1

    def test_incident_create_severity_validation(self):
        from app.schemas.schemas import IncidentCreate
        from pydantic import ValidationError

        # Valid severities
        for sev in ["critical", "high", "medium", "low"]:
            inc = IncidentCreate(title="Test", severity=sev)
            assert inc.severity == sev

        # Invalid severity
        with pytest.raises(ValidationError):
            IncidentCreate(title="Test", severity="extreme")

    def test_incident_response_from_attributes(self):
        from app.schemas.schemas import IncidentResponse

        data = {
            "id": str(uuid.uuid4()),
            "org_id": str(uuid.uuid4()),
            "title": "Test Incident",
            "description": None,
            "severity": "high",
            "status": "open",
            "source": None,
            "ai_summary": None,
            "ai_root_cause": None,
            "ai_confidence": None,
            "assigned_to": None,
            "resolved_at": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        resp = IncidentResponse(**data)
        assert resp.title == "Test Incident"
        assert resp.severity == "high"

    def test_service_create_valid(self):
        from app.schemas.schemas import ServiceCreate

        svc = ServiceCreate(
            name="api-gateway",
            service_type="api",
            environment="production",
        )
        assert svc.name == "api-gateway"

    def test_alert_rule_create(self):
        from app.schemas.schemas import AlertRuleCreate

        rule = AlertRuleCreate(
            name="CPU High",
            condition={"metric": "cpu", "threshold": 90, "operator": ">"},
            severity="critical",
        )
        assert rule.name == "CPU High"
        assert rule.condition["threshold"] == 90

    def test_log_search_params_defaults(self):
        from app.schemas.schemas import LogSearchParams

        params = LogSearchParams()
        assert params.size == 50
        assert params.offset == 0
        assert params.query is None

    def test_org_create_slug_validation(self):
        from app.schemas.schemas import OrgCreate
        from pydantic import ValidationError

        # Valid slug
        org = OrgCreate(name="My Org", slug="my-org-123")
        assert org.slug == "my-org-123"

        # Invalid slug (uppercase)
        with pytest.raises(ValidationError):
            OrgCreate(name="My Org", slug="My_Org")


# ── Unit Tests: Utility Functions ───────────────────────────


class TestUtils:
    """Test frontend-style utility functions replicated for backend."""

    def test_dashboard_overview_schema(self):
        from app.schemas.schemas import DashboardOverview

        overview = DashboardOverview(
            total_services=10,
            healthy_services=8,
            degraded_services=2,
            open_incidents=3,
            critical_incidents=1,
            active_alerts=5,
            logs_ingested_24h=100000,
            ai_sessions_24h=12,
            recent_incidents=[],
            recent_alerts=[],
        )
        assert overview.total_services == 10
        assert overview.healthy_services == 8

    def test_paginated_response(self):
        from app.schemas.schemas import PaginatedResponse

        resp = PaginatedResponse(
            items=["a", "b", "c"],
            total=100,
            page=1,
            page_size=20,
            total_pages=5,
        )
        assert len(resp.items) == 3
        assert resp.total_pages == 5


# ── Integration Tests: FastAPI App ──────────────────────────


class TestHealthEndpoint:
    """Test the health check endpoint."""

    def test_health_check(self):
        from app.main import app

        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "PulseStack AI"
        assert "version" in data
        assert "environment" in data

    def test_openapi_docs_available(self):
        from app.main import app

        client = TestClient(app)
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc_available(self):
        from app.main import app

        client = TestClient(app)
        response = client.get("/redoc")
        assert response.status_code == 200


class TestAuthEndpoints:
    """Test authentication endpoints (no database, validation only)."""

    @needs_db
    def test_register_missing_fields(self):
        from app.main import app

        client = TestClient(app)
        response = client.post("/api/v1/auth/register", json={})
        assert response.status_code == 422  # Validation error

    @needs_db
    def test_register_invalid_email(self):
        from app.main import app

        client = TestClient(app)
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "bad-email", "password": "securepass123", "full_name": "Test"},
        )
        assert response.status_code == 422

    @needs_db
    def test_register_short_password(self):
        from app.main import app

        client = TestClient(app)
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com", "password": "short", "full_name": "Test"},
        )
        assert response.status_code == 422

    @needs_db
    def test_login_missing_fields(self):
        from app.main import app

        client = TestClient(app)
        response = client.post("/api/v1/auth/login", json={})
        assert response.status_code == 422

    def test_protected_endpoint_no_token(self):
        from app.main import app

        client = TestClient(app)
        response = client.get("/api/v1/logs/search")
        # FastAPI OAuth2 returns 401 when no credentials are provided
        assert response.status_code in (401, 403)

    @needs_db
    def test_protected_endpoint_invalid_token(self):
        from app.main import app

        client = TestClient(app)
        response = client.get(
            "/api/v1/logs/search",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert response.status_code == 401

    def test_incidents_no_auth(self):
        from app.main import app

        client = TestClient(app)
        response = client.get("/api/v1/incidents")
        assert response.status_code in (401, 403)

    def test_services_no_auth(self):
        from app.main import app

        client = TestClient(app)
        response = client.get("/api/v1/services")
        assert response.status_code in (401, 403)

    def test_alerts_no_auth(self):
        from app.main import app

        client = TestClient(app)
        response = client.get("/api/v1/alerts")
        assert response.status_code in (401, 403)

    def test_dashboard_no_auth(self):
        from app.main import app

        client = TestClient(app)
        response = client.get("/api/v1/dashboard/overview")
        assert response.status_code in (401, 403)


class TestMiddleware:
    """Test middleware behavior."""

    def test_cors_headers(self):
        from app.main import app

        client = TestClient(app)
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        # Should allow the origin
        assert response.status_code == 200

    def test_request_id_header(self):
        from app.main import app

        client = TestClient(app)
        response = client.get("/health")
        assert "X-Request-ID" in response.headers
        assert "X-Response-Time" in response.headers

    def test_request_id_is_uuid(self):
        from app.main import app

        client = TestClient(app)
        response = client.get("/health")
        request_id = response.headers["X-Request-ID"]
        # Should be a valid UUID
        uuid.UUID(request_id)  # Will raise if invalid


class TestModels:
    """Test SQLAlchemy model definitions."""

    def test_user_model_exists(self):
        from app.models.models import User
        assert User.__tablename__ == "users"

    def test_organization_model_exists(self):
        from app.models.models import Organization
        assert Organization.__tablename__ == "organizations"

    def test_incident_model_exists(self):
        from app.models.models import Incident
        assert Incident.__tablename__ == "incidents"

    def test_alert_model_exists(self):
        from app.models.models import Alert
        assert Alert.__tablename__ == "alerts"

    def test_service_model_exists(self):
        from app.models.models import Service
        assert Service.__tablename__ == "services"

    def test_agent_session_model_exists(self):
        from app.models.models import AgentSession
        assert AgentSession.__tablename__ == "agent_sessions"

    def test_audit_log_model_exists(self):
        from app.models.models import AuditLog
        assert AuditLog.__tablename__ == "audit_logs"

    def test_all_models_inherit_base(self):
        from app.core.database import Base
        from app.models.models import (
            User, Organization, OrgMember, Service,
            Incident, IncidentService, Alert, AlertRule,
            AgentSession, AuditLog,
        )

        for model in [User, Organization, OrgMember, Service,
                       Incident, IncidentService, Alert, AlertRule,
                       AgentSession, AuditLog]:
            assert issubclass(model, Base)
