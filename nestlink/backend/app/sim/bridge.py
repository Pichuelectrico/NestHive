# app/sim/bridge.py
# Gestor de conexiones WebSocket y emisión de snapshots en tiempo real

import json
from typing import List,Set
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast_snapshot(self, snapshot_dict: dict):
        if not self.active_connections:
            return

        dead_connections = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(snapshot_dict)
            except Exception:
                dead_connections.add(connection)

        for dead in dead_connections:
            self.active_connections.discard(dead)
