from starlette.websockets import WebSocket
from services.socket_event import SocketEvent


class ChatRoomCommand(SocketEvent):
    def __init__(self, manager):
        self.manager = manager

    async def execute(self, websocket: WebSocket, data: str):
        await self.manager.chat_room(websocket, data, self.manager)
