import json
from services.socket_event import SocketEvent

class Health(SocketEvent):
    async def handle(self, sio: str, socket_id: str, username: str = None):
        await sio.emit('health', "Alive", room=socket_id)