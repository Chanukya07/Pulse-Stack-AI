"""PulseStack AI — LangGraph Investigation Agent.

Implements a Supervisor-pattern graph that autonomously investigates
incidents by calling tools (log fetcher, clusterer, DB queries) and
synthesising the results into a root-cause report via the configured LLM.

The graph has four sequential nodes:
  1. gather   — pull incident data + logs
  2. cluster  — group logs into patterns
  3. analyse  — LLM synthesises a root-cause hypothesis
  4. report   — format the final output and optionally persist to DB
"""

from __future__ import annotations

import json
import re
import time
from typing import Any

from langgraph.graph import StateGraph, START, END

from app.agents.state import InvestigationState
from app.agents.tools import (
    cluster_logs_tool,
    fetch_incident_tool,
    fetch_logs_tool,
    list_services_tool,
    update_incident_ai_fields,
)
from app.services.ai_service import get_llm_client, SYSTEM_PROMPTS
from app.core.config import get_settings

settings = get_settings()


# ── Node 1: Gather ──────────────────────────────────────────


async def gather_node(state: InvestigationState) -> dict[str, Any]:
    """Pull incident metadata, related logs, and service list."""
    steps: list[str] = list(state.get("steps_taken", []))
    incident_data: dict[str, Any] = {}
    raw_logs: list[dict] = []
    service_info: list[dict] = []

    # Fetch incident from DB if we have an ID
    incident_id = state.get("incident_id")
    if incident_id:
        incident_data = await fetch_incident_tool(incident_id)
        steps.append(f"Fetched incident {incident_id} from database")

    # Fetch logs — use incident title or user query as search term
    query = state.get("query", "")
    search_term = query or incident_data.get("title", "")
    if search_term:
        raw_logs = await fetch_logs_tool(query=search_term, limit=100)
        steps.append(f"Fetched {len(raw_logs)} logs matching '{search_term[:50]}'")

    # Also grab error-level logs if we didn't find much
    if len(raw_logs) < 10:
        error_logs = await fetch_logs_tool(level="error", limit=50)
        raw_logs.extend(error_logs)
        steps.append(f"Added {len(error_logs)} error-level logs for extra context")

    # List services for context
    service_info = await list_services_tool()
    steps.append(f"Listed {len(service_info)} registered services")

    return {
        "incident_data": incident_data,
        "raw_logs": raw_logs,
        "service_info": service_info,
        "steps_taken": steps,
    }


# ── Node 2: Cluster ────────────────────────────────────────


async def cluster_node(state: InvestigationState) -> dict[str, Any]:
    """Cluster raw logs to surface patterns."""
    steps = list(state.get("steps_taken", []))
    raw_logs = state.get("raw_logs", [])

    if not raw_logs:
        steps.append("Skipped clustering — no logs available")
        return {"clustered_logs": {"clusters": []}, "steps_taken": steps}

    n_clusters = min(5, max(1, len(raw_logs) // 10))
    clustered = await cluster_logs_tool(raw_logs, n_clusters=n_clusters)
    n = len(clustered.get("clusters", []))
    steps.append(f"Clustered logs into {n} groups")

    return {"clustered_logs": clustered, "steps_taken": steps}


# ── Node 3: Analyse ────────────────────────────────────────


async def analyse_node(state: InvestigationState) -> dict[str, Any]:
    """Send gathered context to the LLM and ask for root-cause analysis."""
    steps = list(state.get("steps_taken", []))
    incident_data = state.get("incident_data", {})
    raw_logs = state.get("raw_logs", [])
    clustered_logs = state.get("clustered_logs", {})
    service_info = state.get("service_info", [])
    query = state.get("query", "")

    # Build context prompt
    context_parts = []

    if incident_data:
        context_parts.append(
            "## Incident\n" + json.dumps(incident_data, indent=2, default=str)
        )

    if raw_logs:
        log_sample = raw_logs[:30]
        log_text = "\n".join(
            f"[{l.get('timestamp','?')}] [{l.get('level','?').upper()}] "
            f"{l.get('service','?')}: {l.get('message','')}"
            for l in log_sample
        )
        context_parts.append(f"## Recent Logs ({len(raw_logs)} total, showing 30)\n{log_text}")

    if clustered_logs.get("clusters"):
        cluster_summary = []
        for c in clustered_logs["clusters"]:
            sample_msgs = [s.get("message", "")[:120] for s in c.get("samples", [])[:3]]
            cluster_summary.append(
                f"- Cluster {c['cluster_id']} ({c['size']} logs): {'; '.join(sample_msgs)}"
            )
        context_parts.append("## Log Clusters\n" + "\n".join(cluster_summary))

    if service_info:
        svc_text = ", ".join(
            f"{s['name']} ({s['status']})" for s in service_info
        )
        context_parts.append(f"## Registered Services\n{svc_text}")

    context = "\n\n".join(context_parts) if context_parts else "No data sources are currently available. Provide a general analysis based on the query."

    prompt = f"""Investigate the following infrastructure incident.
Provide:
1. **Root Cause** — a concise hypothesis of what went wrong
2. **Evidence** — reference specific log entries, error codes, or patterns
3. **Blast Radius** — which services are affected and how severely
4. **Recommendations** — prioritised remediation steps
5. **Confidence** — your confidence level (0.0 to 1.0) in the root cause

Query: {query}

{context}"""

    try:
        client = get_llm_client()
        model = settings.DEFAULT_LLM_MODEL

        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS["incident_explainer"]},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=2000,
        )

        analysis = response.choices[0].message.content or ""
        steps.append("LLM analysis complete")

        # Try to extract confidence from the response
        confidence = 0.7  # default
        for line in analysis.split("\n"):
            if "confidence" in line.lower():
                nums = re.findall(r"(\d+\.?\d*)", line)
                for n in nums:
                    val = float(n)
                    if val <= 1.0:
                        confidence = val
                        break
                    elif val <= 100:
                        confidence = val / 100.0
                        break

        return {
            "analysis": analysis,
            "root_cause": analysis,
            "confidence": confidence,
            "steps_taken": steps,
        }

    except Exception as e:
        steps.append(f"LLM analysis failed: {e}")
        return {
            "analysis": f"Analysis unavailable: {e}",
            "root_cause": "",
            "confidence": 0.0,
            "error": str(e),
            "steps_taken": steps,
        }


# ── Node 4: Report ─────────────────────────────────────────


async def report_node(state: InvestigationState) -> dict[str, Any]:
    """Compile the final report and optionally update the incident in DB."""
    steps = list(state.get("steps_taken", []))
    incident_data = state.get("incident_data", {})
    analysis = state.get("analysis", "")
    confidence = state.get("confidence", 0.0)
    query = state.get("query", "")
    incident_id = state.get("incident_id")

    # Build markdown report
    parts = [
        "# Investigation Report",
        "",
        f"**Query:** {query}",
    ]

    if incident_data.get("title"):
        parts.append(f"**Incident:** {incident_data['title']}")
        parts.append(f"**Severity:** {incident_data.get('severity', 'unknown')}")

    parts.append(f"**Confidence:** {confidence:.0%}")
    parts.append("")
    parts.append("## Analysis")
    parts.append(analysis)
    parts.append("")
    parts.append("## Steps Taken")
    for i, step in enumerate(steps, 1):
        parts.append(f"{i}. {step}")

    final_report = "\n".join(parts)
    steps.append("Report compiled")

    # Persist to DB if we have an incident ID
    if incident_id and analysis:
        result = await update_incident_ai_fields(
            incident_id=incident_id,
            summary=analysis[:2000],
            root_cause=state.get("root_cause", "")[:2000],
            confidence=confidence,
        )
        if result.get("success"):
            steps.append(f"Updated incident {incident_id} in database")
        else:
            steps.append(f"DB update skipped: {result.get('error', 'unknown')}")

    return {"final_report": final_report, "steps_taken": steps}


# ── Build the Graph ─────────────────────────────────────────


def build_investigation_graph():
    """Construct and compile the investigation agent graph."""
    graph = StateGraph(InvestigationState)

    graph.add_node("gather", gather_node)
    graph.add_node("cluster", cluster_node)
    graph.add_node("analyse", analyse_node)
    graph.add_node("report", report_node)

    graph.add_edge(START, "gather")
    graph.add_edge("gather", "cluster")
    graph.add_edge("cluster", "analyse")
    graph.add_edge("analyse", "report")
    graph.add_edge("report", END)

    return graph.compile()


# ── Public API ──────────────────────────────────────────────


_compiled_graph = None


def get_investigation_graph():
    """Singleton accessor for the compiled graph."""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_investigation_graph()
    return _compiled_graph


async def run_investigation(
    query: str,
    incident_id: str | None = None,
) -> dict[str, Any]:
    """Run the full investigation pipeline and return the result.

    Args:
        query: Natural language description of what to investigate.
        incident_id: Optional incident UUID to pull context from DB.

    Returns:
        Dict with report, analysis, confidence, and steps_taken.
    """
    graph = get_investigation_graph()

    initial_state: InvestigationState = {
        "query": query,
        "incident_id": incident_id,
        "incident_data": {},
        "raw_logs": [],
        "clustered_logs": {},
        "service_info": [],
        "analysis": "",
        "root_cause": "",
        "recommendations": [],
        "confidence": 0.0,
        "final_report": "",
        "steps_taken": [],
        "error": None,
    }

    start = time.time()
    final_state = await graph.ainvoke(initial_state)
    duration_ms = int((time.time() - start) * 1000)

    return {
        "report": final_state.get("final_report", ""),
        "analysis": final_state.get("analysis", ""),
        "root_cause": final_state.get("root_cause", ""),
        "confidence": final_state.get("confidence", 0.0),
        "steps_taken": final_state.get("steps_taken", []),
        "duration_ms": duration_ms,
        "incident_id": incident_id,
    }
