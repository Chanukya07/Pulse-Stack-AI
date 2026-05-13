"""PulseStack AI — AI Agent API Endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.ai_service import summarize_logs, explain_incident, chat, detect_anomalies

router = APIRouter(prefix="/ai", tags=["AI"])


# ── Request/Response Schemas ────────────────────────────


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(..., min_length=1)
    model: str | None = None
    stream: bool = False


class ChatResponse(BaseModel):
    content: str
    model: str
    tokens_used: int = 0


class LogSummarizeRequest(BaseModel):
    logs: list[dict] = Field(..., min_length=1, max_length=200)
    model: str | None = None


class LogSummarizeResponse(BaseModel):
    summary: str
    model: str
    log_count: int
    tokens_used: int = 0


class IncidentExplainRequest(BaseModel):
    incident: dict
    logs: list[dict] | None = None
    model: str | None = None


class AnomalyRequest(BaseModel):
    logs: list[dict] = Field(..., min_length=1, max_length=200)
    model: str | None = None


# ── Endpoints ───────────────────────────────────────────


@router.post("/chat")
async def ai_chat(request: ChatRequest):
    """Conversational AI assistant for infrastructure queries."""
    try:
        if request.stream:
            from fastapi.responses import StreamingResponse
            result_generator = await chat(
                messages=[m.model_dump() for m in request.messages],
                model=request.model,
                stream=True,
            )
            return StreamingResponse(result_generator, media_type="text/event-stream")
            
        result = await chat(
            messages=[m.model_dump() for m in request.messages],
            model=request.model,
            stream=False,
        )
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")


@router.post("/summarize-logs", response_model=LogSummarizeResponse)
async def ai_summarize_logs(request: LogSummarizeRequest):
    """Summarize a batch of log entries using AI."""
    try:
        result = await summarize_logs(request.logs, model=request.model)
        return LogSummarizeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")


@router.post("/explain-incident")
async def ai_explain_incident(request: IncidentExplainRequest):
    """Generate AI explanation for an incident."""
    try:
        result = await explain_incident(
            incident=request.incident,
            logs=request.logs,
            model=request.model,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")


@router.post("/detect-anomalies")
async def ai_detect_anomalies(request: AnomalyRequest):
    """Detect anomalies in log entries using AI."""
    try:
        result = await detect_anomalies(request.logs, model=request.model)
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")


class ClusterLogsRequest(BaseModel):
    logs: list[dict] = Field(..., min_length=1, max_length=1000)
    n_clusters: int = Field(default=5, ge=1, le=20)


@router.post("/cluster-logs")
async def ai_cluster_logs(request: ClusterLogsRequest):
    """Cluster log entries based on their message similarity."""
    from app.services.ai_service import cluster_logs
    try:
        result = await cluster_logs(request.logs, n_clusters=request.n_clusters)
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Clustering error: {str(e)}")


# ── LangGraph Investigation Agent ──────────────────────────


class InvestigateRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000, description="What to investigate")
    incident_id: str | None = Field(None, description="Optional incident UUID for context")


class InvestigateResponse(BaseModel):
    report: str
    analysis: str
    root_cause: str
    confidence: float
    steps_taken: list[str]
    duration_ms: int
    incident_id: str | None = None


@router.post("/investigate", response_model=InvestigateResponse)
async def ai_investigate(request: InvestigateRequest):
    """Run the autonomous LangGraph investigation agent.

    The agent will:
    1. Gather context (incident data, logs, services)
    2. Cluster logs to surface patterns
    3. Analyse findings via LLM
    4. Produce a structured root-cause report
    """
    from app.agents.graph import run_investigation
    try:
        result = await run_investigation(
            query=request.query,
            incident_id=request.incident_id,
        )
        return InvestigateResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Investigation agent error: {str(e)}")

