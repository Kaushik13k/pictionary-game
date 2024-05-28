import json
import logging
import traceback

from init.redis_init import redis_init
from services.socket_event import SocketEvent
from exceptions.exceptions import JoinRoomException

from enums.result_status import ResultStatus
from enums.redis_operations import RedisOperations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JoinRoom(SocketEvent):
    async def handle(self, sio: str, socket_id: str, username: str):
        try:
            logger.info(
                f"Handling join_room event for socket_id {socket_id} and username {username}"
            )
            username = json.loads(username)
            await sio.enter_room(socket_id, username["userName"])

            redis_key = f"room_id:{socket_id}"
            initial_arr_length = redis_init.execute_command(
                RedisOperations.JSON_ARRAY_LENGTH.value, redis_key, ".members"
            )
            redis_init.execute_command(
                RedisOperations.JSON_ARRAY_APPEND.value,
                redis_key,
                ".members",
                json.dumps(username["userName"]),
            )
            updated_arr_length = redis_init.execute_command(
                RedisOperations.JSON_ARRAY_LENGTH.value, redis_key, ".members"
            )
            logger.info(
                f"Increased members array length from {initial_arr_length} to {updated_arr_length}"
            )
            if initial_arr_length < updated_arr_length:
                user = json.loads(
                    redis_init.execute_command(
                        RedisOperations.JSON_GET.value, redis_key
                    )
                )
                logger.info(f"Updated room details in Redis for key {redis_key}")
                await sio.emit(
                    "join_room",
                    {
                        "status": ResultStatus.SUCCESS.value,
                        "room_id": socket_id,
                        "creator": user["creator"],
                        "members": user["members"],
                        "message": f"Successfully joined the room",
                    },
                    room=socket_id,
                )
                logger.info(f"Emitted join_room event for room_id {socket_id}")
            else:
                logger.error(
                    f"Error updating room details in Redis for key {redis_key}"
                )
                raise JoinRoomException(
                    msg=f"Error updating room details in Redis for key {redis_key}"
                )
        except Exception as e:
            logger.error(traceback.format_exc())
            await sio.emit(
                "join_room",
                {
                    "status": ResultStatus.FAILURE.value,
                    "room_id": socket_id,
                    "message": f"Error joining room",
                },
                room=socket_id,
            )
