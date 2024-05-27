import json
import logging

from services.socket_event import SocketEvent
from init.redis_init import redis_init

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JoinRoom(SocketEvent):
    async def handle(self, sio: str, socket_id: str, username: str):
        logger.info(f"Handling join_room event for socket_id {socket_id} and username {username}")
        username = json.loads(username)
        await sio.enter_room(socket_id, username["userName"])

        redis_key = f"room_id:{socket_id}"
        room_details = json.loads(redis_init.get(redis_key))
        logger.info(f"Retrieved room details from Redis for key {redis_key}")

        room_details["members"].append(username["userName"])

        redis_init.set(redis_key, json.dumps(room_details))
        logger.info(f"Updated room details in Redis for key {redis_key}")
        await sio.emit(
            "join_room",
            {
                "room_id": socket_id,
                "creator": username["userName"],
                "members": room_details["members"],
            },
            room=socket_id,
        )
        logger.info(f"Emitted join_room event for room_id {socket_id}")
