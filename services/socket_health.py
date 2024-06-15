from services.socket_event import SocketEvent
from starlette.websockets import WebSocket


class HealthCommand(SocketEvent):
    def __init__(self, manager):
        self.manager = manager

    async def execute(self, websocket: WebSocket, data: str):
        await self.manager.health(websocket, data)
