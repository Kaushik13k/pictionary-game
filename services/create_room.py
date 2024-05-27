import json
from services.socket_event import SocketEvent
from init.redis_init import redis_init

class CreateRoom(SocketEvent):
    async def handle(self, sio, sid, username):
        username = json.loads(username)
        mapping={'creator': username['userName'], 'members': [username['userName']]}
        key=f"room_id:{sid}"
        redis_init.set(key, json.dumps(mapping))
        await sio.emit('create_room', {'room_id': sid, 'creator': username['userName']}, room=sid)