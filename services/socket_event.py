from abc import ABC, abstractmethod
from starlette.websockets import WebSocket


class SocketEvent(ABC):
    @abstractmethod
    async def execute(self, websocket: WebSocket, data: str):
        pass
