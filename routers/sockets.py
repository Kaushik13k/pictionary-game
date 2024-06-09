import json
from starlette.websockets import WebSocket
from fastapi import APIRouter, WebSocketDisconnect
from datetime import datetime
import logging
from typing import Dict, Optional


from enums.socket_operations import SocketOperations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
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

    # async def disconnect(self, websocket: WebSocket):
    #     self.active_connections.remove(websocket)

    async def disconnect(self, client_id: str):
        del self.active_connections[client_id]["socket_instance"]

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


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_id = str(int((datetime.now()).timestamp()))

    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            data_json = json.loads(data)
            operation = data_json.get("operation")

            if operation == SocketOperations.HEALTH.value:
                await manager.health(websocket, data)
            elif operation == "other_operation":
                await manager.other_event(websocket, data)
            else:
                await websocket.send_text("Unknown operation")

    except WebSocketDisconnect:
        manager.disconnect(client_id)
        await manager.broadcast(f"Client #{client_id} left the chat")
