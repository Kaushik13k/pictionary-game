import json
import asyncio
import logging
from datetime import datetime
from starlette.websockets import WebSocket
from fastapi import APIRouter, WebSocketDisconnect

from events.start_game import StartCommand
from events.chat_room import ChatRoomCommand
from events.socket_health import HealthCommand
from events.drawing_canvas import CanvasCommand
from events.selected_word import SelectedWordCommand
from enums.socket_operations import SocketOperations
from services.connection_manager import ConnectionManager


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(lineno)d",
)
logger = logging.getLogger(__name__)

router = APIRouter()


class CommandHandler:
    def __init__(self, manager: ConnectionManager):
        self.commands = {
            SocketOperations.HEALTH.value: HealthCommand(manager),
            SocketOperations.CANVAS.value: CanvasCommand(manager),
            SocketOperations.START_GAME.value: StartCommand(manager),
            SocketOperations.CHAT_ROOM.value: ChatRoomCommand(manager),
            SocketOperations.SELECTED_WORD.value: SelectedWordCommand(manager),
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
                asyncio.create_task(command.execute(websocket, data))
            else:
                await websocket.send_text("Unknown event")

    except WebSocketDisconnect:
        await manager.disconnect(client_id)
