import json
import logging
import traceback

from routers.sockets import manager
from templates.room_events import RoomEvents
from utils.api_response import success, error
from redis_json.redis_operations import RedisJson
from exceptions.exceptions import JoinRoomException

from enums.redis_keys import RedisIdentityKeys
from enums.redis_locations import RedisLocations
from enums.socket_operations import SocketOperations
from enums.messages import EventSuccessMessages, EventFailedMessages


logger = logging.getLogger(__name__)


class JoinRoom(RoomEvents):
    async def handle_room(self):
        try:
            logger.info(
                f"Handling join_room event for socket_id and username {self.room_data.player_name} and room_id {self.room_data.room_id}, sid {self.room_data.sid}"
            )

            redis_key = f"{RedisIdentityKeys.PLAYERS.value}:{self.room_data.room_id}"
            initial_arr_length = RedisJson().length(
                redis_key=redis_key, location=RedisLocations.MEMBERS.value
            )
            if not initial_arr_length:
                logger.error(
                    f"Error getting initial array length from Redis for key {redis_key}"
                )
                raise JoinRoomException(
                    msg=f"Error getting initial array length from Redis."
                )

            latest_player_id = int(
                (
                    RedisJson().get(
                        redis_key=redis_key, location=".members[-1].player_id"
                    )
                ).decode("utf-8")
            )
            if not latest_player_id:
                logger.error(
                    f"Error getting latest player-id from Redis for key {redis_key}"
                )
                raise JoinRoomException(
                    msg=f"Error getting latest player-id from Redis."
                )

            redis_value = {
                "player_id": latest_player_id + 1,
                "is_active": True,
                "player_name": self.room_data.player_name,
                "score": 0,
                "is_creator": False,
                "sid": self.room_data.sid,
            }
            append_result = RedisJson().append(
                redis_key=redis_key,
                location=RedisLocations.MEMBERS.value,
                redis_value=redis_value,
            )
            if not append_result:
                logger.error(
                    f"Error appending room details in Redis for key {redis_key}"
                )
                raise JoinRoomException(msg=f"Error appending room details in Redis.")

            logger.info(f"Appended player to the room with key {redis_key}")
            updated_arr_length = RedisJson().length(
                redis_key=redis_key, location=RedisLocations.MEMBERS.value
            )
            if not initial_arr_length:
                logger.error(
                    f"Error getting updated array length from Redis for key {redis_key}"
                )
                raise JoinRoomException(
                    msg=f"Error getting updated array length from Redis."
                )

            if not initial_arr_length < updated_arr_length:
                logger.error(
                    f"Error updating room details in Redis for key {redis_key}"
                )
                raise JoinRoomException(msg=f"Error updating room details in Redis.")

            await manager.activate_connection(self.room_data.sid)
            await manager.send_personal_message(
                {
                    "event": SocketOperations.JOIN.value,
                    "value": EventSuccessMessages.ROOM_JOIN_SUCCESS.value,
                },
                self.room_data.sid,
            )

            await manager.broadcast(
                {
                    "event": SocketOperations.JOIN.value,
                    "value": f"{self.room_data.player_name} has joined the room.",
                },
                self.room_data.sid,
            )

            return success(
                {
                    "player_id": latest_player_id + 1,
                    "is_creator": False,
                },
                message=EventSuccessMessages.ROOM_JOIN_SUCCESS.value,
            )

        except Exception as e:
            logger.error(f"Error joining room: {e}")
            logger.error(traceback.format_exc())
            return error({"success": False})
