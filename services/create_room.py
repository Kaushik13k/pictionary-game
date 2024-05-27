import json
import logging
from services.socket_event import SocketEvent
from init.redis_init import redis_init

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CreateRoom(SocketEvent):
    async def handle(self, sio: str, socket_id: str, username: str):
        logger.info(f"Handling create_room event for socket_id {socket_id} and username {username}")
        username = json.loads(username)
        user_data = {"creator": username["userName"], "members": [username["userName"]]}
        redis_key = f"room_id:{socket_id}"
        redis_init.set(redis_key, json.dumps(user_data))
        logger.info(f"Set data in Redis for key {redis_key}")
        await sio.emit(
            "create_room",
            {"room_id": socket_id, "creator": username["userName"]},
            room=socket_id,
        )
        logger.info(f"Emitted create_room event for room_id {socket_id}")
