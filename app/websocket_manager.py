from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from typing import List, Dict
from app.models import User

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[WebSocket, Dict[str, User]] = {}

    async def connect(self, websocket: WebSocket, user: User):
        if not user:
            raise HTTPException(status_code=403, detail="Authentication required")
        await websocket.accept()
        self.active_connections[websocket] = {"user": user}

    def disconnect(self, websocket: WebSocket):
        self.active_connections.pop(websocket, None)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
    
    async def broadcast_to_moderators(self, message: str):
        for websocket, info in self.active_connections.items():
            if info["user"].is_moderator:  # Only send to moderators
                await websocket.send_text(message)

# Instantiate the manager
manager = ConnectionManager()