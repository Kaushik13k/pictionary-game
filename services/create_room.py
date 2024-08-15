import logging
import traceback
from fastapi import APIRouter

from routers.sockets import manager
from templates.room_events import RoomEvents
from utils.api_response import success, error
from redis_json.redis_operations import RedisJson
from exceptions.exceptions import CreateRoomException

from enums.redis_locations import RedisLocations
from enums.socket_operations import SocketOperations
from enums.messages import EventSuccessMessages, EventFailedMessages

router = APIRouter()
logger = logging.getLogger(__name__)


class CreateRoom(RoomEvents):
    async def handle_room(self):
        """
        Handle the creation of a new room event.

        This method generates a unique room ID and sets the room data in Redis.

        Returns:
            dict: A success response with room details(room_id, is_creator, player_id) if the room is created successfully.
            dict: An error response if there is a failure in creating the room.
        """
        try:
            room_id = self.generate_unique_room_id()

            logger.info(
                f"Handling create_room event for username {self.room_data.player_name}"
            )
            user_data = {
                "creator": 1,
                "members": [
                    {
                        "player_id": 1,
                        "is_active": True,
                        "player_name": self.room_data.player_name,
                        "score": 0,
                        "is_creator": True,
                        "sid": self.room_data.sid,
                    }
                ],
            }
            redis_key = f"room_id_players:{room_id}"
            result = RedisJson().set(
                redis_key=redis_key,
                redis_value=user_data,
                location=RedisLocations.ROOT.value,
            )

            if result:
                logger.info(
                    f"Room created and data set successfully for key {redis_key}"
                )

                await manager.activate_connection(self.room_data.sid)
                await manager.send_personal_message(
                    {
                        "event": SocketOperations.CREATE.value,
                        "value": EventSuccessMessages.ROOM_CREATION_SUCCESS.value,
                    },
                    self.room_data.sid,
                )
                return success(
                    {
                        "room_id": room_id,
                        "is_creator": True,
                        "player_id": user_data["members"][0]["player_id"],
                    },
                    message=EventSuccessMessages.ROOM_CREATION_SUCCESS.value,
                )

            else:
                raise CreateRoomException(
                    msg=f"Error creating room details in Redis for key {redis_key}"
                )
        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())
            return error(EventFailedMessages.ROOM_CREATION_FAILED.value)
