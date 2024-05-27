from abc import ABC, abstractmethod

class SocketEvent(ABC):
    @abstractmethod
    async def handle(self, sio, sid, data):
        pass