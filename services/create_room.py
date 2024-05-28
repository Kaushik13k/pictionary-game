import json
import logging
import traceback

from init.redis_init import redis_init
from services.socket_event import SocketEvent
from exceptions.exceptions import CreateRoomException

from enums.result_status import ResultStatus
from enums.redis_operations import RedisOperations
from enums.socket_operations import SocketOperations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CreateRoom(SocketEvent):
    async def handle(self, sio: str, socket_id: str, username: str):
        try:
            logger.info(
                f"Handling create_room event for socket_id {socket_id} and username {username}"
            )
            username = json.loads(username)
            user_data = {
                "creator": username["userName"],
                "members": [username["userName"]],
            }
            redis_key = f"room_id:{socket_id}"
            result = redis_init.execute_command(
                RedisOperations.JSON_SET.value, redis_key, "$", json.dumps(user_data)
            )
            if result.decode("utf-8") == "OK":
                logger.info(f"Set data in Redis for key {redis_key}")
                await sio.emit(
                    SocketOperations.CREATE.value,
                    {
                        "status": ResultStatus.SUCCESS.value,
                        "room_id": socket_id,
                        "creator": username["userName"],
                        "members": user_data["members"],
                        "message": f"Room Created",
                    },
                    room=socket_id,
                )
                logger.info(f"Emitted create_room event for room_id {socket_id}")
            else:
                raise CreateRoomException(
                    msg=f"Error creating room details in Redis for key {redis_key}"
                )
        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())
            await sio.emit(
                SocketOperations.CREATE.value,
                {
                    "status": ResultStatus.FAILURE.value,
                    "room_id": socket_id,
                    "message": f"Error creating room",
                },
                room=socket_id,
            )
