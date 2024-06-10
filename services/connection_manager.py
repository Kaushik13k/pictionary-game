from starlette.websockets import WebSocket
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConnectionManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConnectionManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = {
            "socket_instance": websocket,
            "connected": False,
        }

        await websocket.send_text(f"{client_id}")

    async def activate_connection(self, client_id: str):
        self.active_connections[client_id]["connected"] = True

    async def disconnect(self, client_id: str):
        del self.active_connections[client_id]

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def health(self, websocket: WebSocket, message: str):
        await websocket.send_text("Health check successful")

    async def send_personal_message(self, message: str, client_id: str):
        logger.info(f"Sending message to {client_id}")
        logger.info(f"Active connections: {self.active_connections}")
        await self.active_connections[client_id]["socket_instance"].send_text(message)

    async def broadcast(self, message: str, exclude: Optional[str] = None):
        for client_id, connection in self.active_connections.items():
            if client_id != exclude and connection["connected"]:
                await connection["socket_instance"].send_text(message)