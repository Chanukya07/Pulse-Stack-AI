"""
PulseStack AI — Main Application Entry Point

Autonomous AI-Powered Observability & Incident Intelligence Platform
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1 import agents, auth, alerts, dashboard, incidents, logs, services, websocket
from app.core.config import get_settings
from app.core.elasticsearch import ensure_log_index
from app.core.middleware import setup_middleware

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"   Environment: {settings.ENVIRONMENT}")

    # Ensure Elasticsearch indices exist
    try:
        await ensure_log_index()
        print("   Elasticsearch index ready")
    except Exception as e:
        print(f"   Elasticsearch not available: {e}")

    yield

    # Shutdown
    print(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Autonomous AI-Powered Observability & Incident Intelligence Platform",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    lifespan=lifespan,
)

# Middleware
setup_middleware(app)

# API v1 Routes
api_prefix = settings.API_V1_PREFIX
app.include_router(auth.router, prefix=api_prefix)
app.include_router(logs.router, prefix=api_prefix)
app.include_router(incidents.router, prefix=api_prefix)
app.include_router(alerts.router, prefix=api_prefix)
app.include_router(services.router, prefix=api_prefix)
app.include_router(dashboard.router, prefix=api_prefix)
app.include_router(agents.router, prefix=api_prefix)
app.include_router(websocket.router, prefix=api_prefix)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for load balancers and Kubernetes probes."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }
