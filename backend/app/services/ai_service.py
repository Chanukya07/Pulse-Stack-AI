"""PulseStack AI — LLM Service Layer (OpenAI / Ollama)."""

from typing import AsyncGenerator
import json

from openai import AsyncOpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

from app.core.config import get_settings

settings = get_settings()

# Initialize OpenAI client (works with Ollama too via base_url)
_client: AsyncOpenAI | None = None


def get_llm_client() -> AsyncOpenAI:
    """Get or create the async OpenAI client."""
    global _client
    if _client is None:
        if settings.DEFAULT_LLM_PROVIDER == "ollama":
            _client = AsyncOpenAI(
                base_url=settings.OLLAMA_BASE_URL + "/v1",
                api_key="ollama",  # Ollama doesn't need a real key
            )
        elif settings.DEFAULT_LLM_PROVIDER == "openrouter":
            _client = AsyncOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=settings.OPENAI_API_KEY, # Reusing the API key setting for OpenRouter key
            )
        else:
            _client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


SYSTEM_PROMPTS = {
    "log_summarizer": """You are an expert SRE and DevOps engineer analyzing infrastructure logs.
Given a set of log entries, provide:
1. A concise summary of what happened
2. Key patterns or anomalies detected
3. Severity assessment (critical/high/medium/low)
4. Recommended actions

Be precise and technical. Reference specific services, error codes, and timestamps.""",

    "incident_explainer": """You are an expert incident response engineer.
Given incident details and related logs, explain:
1. What went wrong (root cause hypothesis)
2. Timeline of events
3. Affected services and blast radius
4. Recommended remediation steps

Be clear, actionable, and prioritize by impact.""",

    "assistant": """You are PulseStack AI, an intelligent infrastructure assistant embedded directly within the PulseStack monitoring platform.
You help engineers understand their systems by analyzing logs, metrics, and incidents.
You have deep expertise in Distributed systems, Kubernetes, PostgreSQL, Redis, and security monitoring.

IMPORTANT CONTEXT FOR YOU:
- You are directly integrated into the user's PulseStack dashboard.
- If a user asks you to "change an alert" or "update a threshold" or "check logs", you should respond as if you have access to their PulseStack environment. Do NOT ask them "which monitoring system are you using?" or "what is the scope?", because you are already in their system.
- Even if you cannot physically execute the action (you are read-only for now), you should confidently acknowledge the request and explain what data from PulseStack you would change, rather than asking them clarifying questions about their infrastructure stack.

Be concise, technical, and actionable.""",

    "anomaly_detector": """You are a log anomaly detection specialist.
Analyze the provided logs and identify:
1. Unusual patterns or spikes
2. New error types not seen before
3. Performance degradations
4. Security-relevant events
Rate each anomaly's severity and confidence level.""",
}


async def summarize_logs(logs: list[dict], model: str | None = None) -> dict:
    """Summarize a batch of log entries using LLM."""
    client = get_llm_client()
    model = model or settings.DEFAULT_LLM_MODEL

    # Format logs for the prompt
    log_text = "\n".join(
        f"[{log.get('timestamp', 'N/A')}] [{log.get('level', 'info').upper()}] "
        f"{log.get('service', 'unknown')}: {log.get('message', '')}"
        for log in logs[:100]  # Cap at 100 logs to stay within context
    )

    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPTS["log_summarizer"]},
            {"role": "user", "content": f"Analyze these infrastructure logs:\n\n{log_text}"},
        ],
        temperature=0.3,
        max_tokens=1000,
    )

    return {
        "summary": response.choices[0].message.content or "",
        "model": model,
        "log_count": len(logs),
        "tokens_used": response.usage.total_tokens if response.usage else 0,
    }


async def explain_incident(incident: dict, logs: list[dict] | None = None, model: str | None = None) -> dict:
    """Generate AI explanation for an incident."""
    client = get_llm_client()
    model = model or settings.DEFAULT_LLM_MODEL

    context = f"""Incident: {incident.get('title', 'Unknown')}
Severity: {incident.get('severity', 'unknown')}
Status: {incident.get('status', 'open')}
Description: {incident.get('description', 'No description')}"""

    if logs:
        log_text = "\n".join(
            f"[{log.get('timestamp')}] [{log.get('level', '').upper()}] "
            f"{log.get('service', '')}: {log.get('message', '')}"
            for log in logs[:50]
        )
        context += f"\n\nRelated Logs:\n{log_text}"

    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPTS["incident_explainer"]},
            {"role": "user", "content": context},
        ],
        temperature=0.3,
        max_tokens=1500,
    )

    return {
        "explanation": response.choices[0].message.content or "",
        "model": model,
        "tokens_used": response.usage.total_tokens if response.usage else 0,
    }


async def chat(
    messages: list[dict],
    model: str | None = None,
    stream: bool = False,
) -> dict | AsyncGenerator[str, None]:
    """Conversational AI assistant."""
    client = get_llm_client()
    model = model or settings.DEFAULT_LLM_MODEL

    full_messages = [
        {"role": "system", "content": SYSTEM_PROMPTS["assistant"]},
        *messages,
    ]

    if stream:
        return _stream_chat(client, model, full_messages)

    response = await client.chat.completions.create(
        model=model,
        messages=full_messages,
        temperature=0.5,
        max_tokens=2000,
    )

    return {
        "content": response.choices[0].message.content or "",
        "model": model,
        "tokens_used": response.usage.total_tokens if response.usage else 0,
    }


async def _stream_chat(
    client: AsyncOpenAI, model: str, messages: list[dict]
) -> AsyncGenerator[str, None]:
    """Stream chat response token by token."""
    stream = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.5,
        max_tokens=2000,
        stream=True,
        stream_options={"include_usage": True},
    )
    async for chunk in stream:
        if len(chunk.choices) > 0 and chunk.choices[0].delta.content:
            data = json.dumps({"content": chunk.choices[0].delta.content})
            yield f"data: {data}\n\n"
        
        if chunk.usage:
            # Handle standard OpenAI / OpenRouter usage object to get reasoning tokens
            usage_dict = chunk.usage.model_dump() if hasattr(chunk.usage, 'model_dump') else chunk.usage
            reasoning_tokens = 0
            if isinstance(usage_dict, dict):
                details = usage_dict.get("completion_tokens_details") or {}
                reasoning_tokens = details.get("reasoning_tokens") or usage_dict.get("reasoning_tokens", 0)
                
            data = json.dumps({
                "usage": {
                    "total_tokens": chunk.usage.total_tokens,
                    "reasoning_tokens": reasoning_tokens
                }
            })
            yield f"data: {data}\n\n"


async def detect_anomalies(logs: list[dict], model: str | None = None) -> dict:
    """Detect anomalies in log entries."""
    client = get_llm_client()
    model = model or settings.DEFAULT_LLM_MODEL

    log_text = "\n".join(
        f"[{log.get('timestamp')}] [{log.get('level', '').upper()}] "
        f"{log.get('service', '')}: {log.get('message', '')}"
        for log in logs[:100]
    )

    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPTS["anomaly_detector"]},
            {"role": "user", "content": f"Analyze these logs for anomalies:\n\n{log_text}"},
        ],
        temperature=0.2,
        max_tokens=1500,
    )

    return {
        "analysis": response.choices[0].message.content or "",
        "model": model,
        "log_count": len(logs),
        "tokens_used": response.usage.total_tokens if response.usage else 0,
    }


async def create_embeddings(texts: list[str], model: str | None = None) -> list[list[float]]:
    """Create vector embeddings for a list of texts."""
    client = get_llm_client()
    model = model or settings.EMBEDDING_MODEL

    response = await client.embeddings.create(
        input=texts,
        model=model,
    )

    return [data.embedding for data in response.data]


async def cluster_logs(logs: list[dict], n_clusters: int = 5) -> dict:
    """Cluster log messages using TF-IDF and KMeans."""
    if not logs:
        return {"clusters": []}
    
    messages = [log.get("message", "") for log in logs]
    
    # If there are fewer logs than requested clusters, reduce clusters
    actual_clusters = min(n_clusters, len(set(messages)))
    if actual_clusters < 1:
        return {"clusters": []}

    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    X = vectorizer.fit_transform(messages)

    kmeans = KMeans(n_clusters=actual_clusters, random_state=42, n_init="auto")
    labels = kmeans.fit_predict(X)

    # Group logs by cluster
    clusters = {}
    for idx, label in enumerate(labels):
        label_id = int(label)
        if label_id not in clusters:
            clusters[label_id] = {
                "cluster_id": label_id,
                "size": 0,
                "samples": [],
            }
        
        clusters[label_id]["size"] += 1
        if len(clusters[label_id]["samples"]) < 5:
            clusters[label_id]["samples"].append(logs[idx])

    return {"clusters": list(clusters.values())}

