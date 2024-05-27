import json
from services.socket_event import SocketEvent
from init.redis_init import redis_init

class JoinRoom(SocketEvent):
    async def handle(self, sio, sid, username):
        username = json.loads(username)
        await sio.enter_room(sid, username["userName"])

        key = f"room_id:{sid}"
        room_details = json.loads(redis_init.get(key))

        room_details['members'].append(username["userName"])

        redis_init.set(key, json.dumps(room_details))
        await sio.emit('join_room', {'room_id': sid, 'creator': username['userName'], 'members': room_details['members']}, room=sid)