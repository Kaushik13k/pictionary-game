import json
import logging
from datetime import datetime
from starlette.websockets import WebSocket
from fastapi import APIRouter, WebSocketDisconnect
from routers.start_game import StartCommand
from services.connection_manager import ConnectionManager
from enums.socket_operations import SocketOperations
from routers.socket_health import HealthCommand

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


class CommandHandler:
    def __init__(self, manager: ConnectionManager):
        self.commands = {
            SocketOperations.HEALTH.value: HealthCommand(manager),
            SocketOperations.START_GAME.value: StartCommand(manager),
        }

    def get_command(self, operation: str):
        return self.commands.get(operation)


manager = ConnectionManager()
command_handler = CommandHandler(manager)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_id = str(int((datetime.now()).timestamp()))

    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            data_json = json.loads(data)
            event = data_json.get("event")

            command = command_handler.get_command(event)
            if command:
                await command.execute(websocket, data)
            else:
                await websocket.send_text("Unknown event")

    except WebSocketDisconnect:
        manager.disconnect(client_id)
        await manager.broadcast(f"Client #{client_id} left the chat")
