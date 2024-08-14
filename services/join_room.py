import json
import logging
import traceback

from init.redis_init import redis_init
from init.socket_init import socket_io
from templates.room_events import RoomEvents
from enums.redis_operations import RedisOperations
from exceptions.exceptions import JoinRoomException
from utils.api_response import success, error

from routers.sockets import manager


logger = logging.getLogger(__name__)


class JoinRoom(RoomEvents):
    async def handle_room(self):
        try:
            logger.info(
                f"Handling join_room event for socket_id and username {self.room_data.player_name} and room_id {self.room_data.room_id}, sid {self.room_data.sid}"
            )

            redis_key = f"room_id_players:{self.room_data.room_id}"
            initial_arr_length = redis_init.execute_command(
                RedisOperations.JSON_ARRAY_LENGTH.value, redis_key, ".members"
            )

            members_json = redis_init.execute_command(
                RedisOperations.JSON_GET.value,
                redis_key,
                ".members",
            )
            members = json.loads(members_json)
            players_sids = [member["sid"] for member in members]
            logger.info(f"Players sids: {players_sids}")

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
                        "is_creator": False,
                        "sid": self.room_data.sid,
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

                # Emit 'joinedRoom' event to the player who just joined
                await manager.activate_connection(self.room_data.sid)
                await manager.send_personal_message(
                    {"event": "join_room", "value": "Joined The Room"},
                    self.room_data.sid,
                )

                # Emit 'playerJoined' event to all other players in the room
                await manager.broadcast(
                    {
                        "event": "join_room",
                        "value": f"{self.room_data.player_name} has joined the room.",
                    },
                    self.room_data.sid,
                )

                return success(
                    {
                        "player_id": latest_player_id + 1,
                        "is_creator": False,
                    },
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
