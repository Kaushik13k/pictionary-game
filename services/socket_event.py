from abc import ABC, abstractmethod

class SocketEvent(ABC):
    @abstractmethod
    async def handle(self, sio, socket_id, data):
        pass