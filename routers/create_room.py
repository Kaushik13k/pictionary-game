from fastapi import APIRouter
from pydantic import BaseModel
import uuid
import logging
import json
import logging
import traceback


from init.redis_init import redis_init
from exceptions.exceptions import CreateRoomException

from enums.redis_operations import RedisOperations

router = APIRouter()
logger = logging.getLogger(__name__)

class Room(BaseModel):
    rounds: int
    time: int
    player_name: str
    max_players_count: int
    hints: int
    word_count: int


def generate_unique_room_id():
    return str(uuid.uuid4())

def generate_socket_link(room_id):
    return f"ws://0.0.0.0:8000/{room_id}"

@router.post("/create-room", tags=["Heath"], responses={404: {"description": "Not found"}})
async def create_room(room: Room):
    try:
        room_id = generate_unique_room_id()
        socket_link = generate_socket_link(room_id)

        logger.info(
            f"Handling create_room event for socket_id {socket_link} and username {room.player_name}"
        )
        # username = json.loads(username)
        user_data = {
            "creator": 1,
            "members": [{"player_id": 1, "is_active": True, "player_name": room.player_name, "score": 0}],
        }
        redis_key = f"room_id_players:{room_id}"
        result = redis_init.execute_command(
            RedisOperations.JSON_SET.value, redis_key, "$", json.dumps(user_data)
        )
        if result.decode("utf-8") == "OK":
            logger.info(f"Set data in Redis for key {redis_key}")
            return {'room-id': room_id, 'socket-link': socket_link}
        
        else:
            raise CreateRoomException(
                msg=f"Error creating room details in Redis for key {redis_key}"
            )
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return {'message': 'ERROR'}