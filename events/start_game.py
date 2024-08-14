from starlette.websockets import WebSocket
from services.socket_event import SocketEvent


class StartCommand(SocketEvent):
    def __init__(self, manager):
        self.manager = manager

    async def execute(self, websocket: WebSocket, data: str):
        await self.manager.start_game(websocket, data, self.manager)
