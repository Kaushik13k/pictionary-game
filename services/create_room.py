import json
import logging
import traceback
from fastapi import APIRouter

from init.redis_init import redis_init
from init.socket_init import socket_io
from services.room_events import RoomEvents
from utils.api_response import success, error
from enums.redis_operations import RedisOperations
from exceptions.exceptions import CreateRoomException


router = APIRouter()
logger = logging.getLogger(__name__)


class CreateRoom(RoomEvents):
    async def handle_room(self):
        try:
            # room_id = self.generate_unique_room_id()
            socket_link = self.generate_socket_link(self.room_data.sid)

            logger.info(
                f"Handling create_room event for socket_id {socket_link} and username {self.room_data.player_name}"
            )
            user_data = {
                "creator": 1,
                "members": [
                    {
                        "player_id": 1,
                        "is_active": True,
                        "player_name": self.room_data.player_name,
                        "score": 0,
                    }
                ],
            }
            redis_key = f"room_id_players:{self.room_data.sid}"
            result = redis_init.execute_command(
                RedisOperations.JSON_SET.value, redis_key, "$", json.dumps(user_data)
            )
            if result.decode("utf-8") == "OK":
                logger.info(f"Set data in Redis for key {redis_key}")
                await socket_io.emit(
                    "create_room",
                    {
                        "room_id": self.room_data.sid,
                        "mesasge": f"Room created successfully, {self.room_data.player_name} joined the room",
                    },
                    room=self.room_data.sid,
                )
                return success(
                    {
                        "room_id": self.room_data.sid,
                        "socket_link": socket_link,
                        "is_creator": True,
                        "player_id": user_data["members"][0]["player_id"],
                    },
                    message="Rooms fetched successfully",
                )

            else:
                raise CreateRoomException(
                    msg=f"Error creating room details in Redis for key {redis_key}"
                )
        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())
            return error("Failed to create room")
