import json
from services.socket_event import SocketEvent
from init.redis_init import redis_init


class JoinRoom(SocketEvent):
    async def handle(self, sio: str, socket_id: str, username: str):
        username = json.loads(username)
        await sio.enter_room(socket_id, username["userName"])

        redis_key = f"room_id:{socket_id}"
        room_details = json.loads(redis_init.get(redis_key))

        room_details["members"].append(username["userName"])

        redis_init.set(redis_key, json.dumps(room_details))
        await sio.emit(
            "join_room",
            {
                "room_id": socket_id,
                "creator": username["userName"],
                "members": room_details["members"],
            },
            room=socket_id,
        )
