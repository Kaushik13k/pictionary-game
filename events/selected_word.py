from starlette.websockets import WebSocket
from templates.socket_events import SocketEvent
from services.connection_manager import ConnectionManager


class SelectedWordCommand(SocketEvent):
    def __init__(self, manager: ConnectionManager):
        self.manager = manager

    async def execute(self, websocket: WebSocket, data: str):
        await self.manager.selected_word(websocket, data, self.manager)
