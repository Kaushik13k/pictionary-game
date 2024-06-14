from services.socket_event import SocketEvent
from starlette.websockets import WebSocket


class StartCommand(SocketEvent):
    def __init__(self, manager):
        self.manager = manager

    async def execute(self, websocket: WebSocket, data: str):
        await self.manager.start_game(websocket, data)
