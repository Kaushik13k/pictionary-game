import json
from services.socket_event import SocketEvent
from init.redis_init import redis_init

class Health(SocketEvent):
    async def handle(self, sio, sid, username=None):
        print(f'Received ping from {sid}')
        await sio.emit('health', "Alive", room=sid)