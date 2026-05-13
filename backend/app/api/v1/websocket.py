"""PulseStack AI — WebSocket Live Log Streaming."""

import asyncio
import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["WebSocket"])


class ConnectionManager:
    """Manages WebSocket connections for live log streaming."""

    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel: str = "logs"):
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(websocket)

    def disconnect(self, websocket: WebSocket, channel: str = "logs"):
        if channel in self.active_connections:
            self.active_connections[channel] = [
                ws for ws in self.active_connections[channel] if ws != websocket
            ]

    async def broadcast(self, message: dict[str, Any], channel: str = "logs"):
        """Broadcast a message to all connections on a channel."""
        if channel not in self.active_connections:
            return
        disconnected = []
        for ws in self.active_connections[channel]:
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.disconnect(ws, channel)

    @property
    def connection_count(self) -> int:
        return sum(len(conns) for conns in self.active_connections.values())


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws/logs")
async def websocket_log_stream(websocket: WebSocket):
    """Live log stream via WebSocket. Clients receive real-time log entries."""
    await manager.connect(websocket, "logs")
    try:
        while True:
            # Keep connection alive; client can send filter commands
            data = await websocket.receive_text()
            try:
                command = json.loads(data)
                # Could handle filter commands here (service, level, etc.)
                await websocket.send_json({"type": "ack", "command": command})
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})
    except WebSocketDisconnect:
        manager.disconnect(websocket, "logs")


@router.websocket("/ws/incidents")
async def websocket_incident_stream(websocket: WebSocket):
    """Live incident updates via WebSocket."""
    await manager.connect(websocket, "incidents")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, "incidents")


@router.websocket("/ws/alerts")
async def websocket_alert_stream(websocket: WebSocket):
    """Live alert updates via WebSocket."""
    await manager.connect(websocket, "alerts")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, "alerts")
