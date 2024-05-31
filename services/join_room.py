import json
import logging
import traceback

from init.redis_init import redis_init
from services.room_events import RoomEvents
from enums.redis_operations import RedisOperations
from exceptions.exceptions import JoinRoomException
from utils.api_response import success, error


logger = logging.getLogger(__name__)


class JoinRoom(RoomEvents):
    async def handle_room(self):
        try:
            logger.info(
                f"Handling join_room event for socket_id and username {self.room_data.player_name}"
            )

            redis_key = f"room_id_players:{self.room_data.room_id}"
            initial_arr_length = redis_init.execute_command(
                RedisOperations.JSON_ARRAY_LENGTH.value, redis_key, ".members"
            )
            latest_player_id = int(
                (
                    redis_init.execute_command(
                        RedisOperations.JSON_GET.value,
                        redis_key,
                        ".members[-1].player_id",
                    )
                ).decode("utf-8")
            )
            logger.info(f"Latest player id: {latest_player_id}")

            redis_init.execute_command(
                RedisOperations.JSON_ARRAY_APPEND.value,
                redis_key,
                ".members",
                json.dumps(
                    {
                        "player_id": latest_player_id + 1,
                        "is_active": True,
                        "player_name": self.room_data.player_name,
                        "score": 0,
                    }
                ),
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
                socket_link = self.generate_socket_link(self.room_data.room_id)
                return success(
                    {"socket_link": socket_link},
                    message="Rooms fetched successfully",
                )
            else:
                logger.error(
                    f"Error updating room details in Redis for key {redis_key}"
                )
                raise JoinRoomException(
                    msg=f"Error updating room details in Redis for key {redis_key}"
                )
        except Exception as e:
            logger.error(traceback.format_exc())
            return error({"success": False})
