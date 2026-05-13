"""PulseStack AI — Agent State Schema.

Defines the typed state that flows through the LangGraph investigation graph.
Uses TypedDict for LangGraph compatibility.
"""

from __future__ import annotations

from typing import Any, TypedDict


class InvestigationState(TypedDict, total=False):
    """State carried through every node of the investigation graph."""

    # ── Input ───────────────────────────────────────────────
    query: str
    incident_id: str | None

    # ── Gathered Context ────────────────────────────────────
    incident_data: dict[str, Any]
    raw_logs: list[dict[str, Any]]
    clustered_logs: dict[str, Any]
    service_info: list[dict[str, Any]]

    # ── Agent Reasoning ─────────────────────────────────────
    analysis: str
    root_cause: str
    recommendations: list[str]
    confidence: float

    # ── Final Output ────────────────────────────────────────
    final_report: str
    steps_taken: list[str]
    error: str | None
