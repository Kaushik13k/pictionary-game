from fastapi import APIRouter
from pydantic import BaseModel
import uuid
import logging
import json
import logging
import traceback
from exceptions.exceptions import JoinRoomException


from init.redis_init import redis_init

from enums.redis_operations import RedisOperations

router = APIRouter()
logger = logging.getLogger(__name__)

class JoinRoom(BaseModel):
    player_name: str
    room_id: str

def generate_unique_room_id():
    return str(uuid.uuid4())

def generate_socket_link(room_id):
    return f"ws://0.0.0.0:8000/{room_id}"

@router.post("/join-room", tags=["Heath"], responses={404: {"description": "Not found"}})
async def join_room(join_room: JoinRoom):
    try:
        logger.info(
            f"Handling join_room event for socket_id and username {join_room.player_name}"
        )
        # username = json.loads(username)
        # await sio.enter_room(socket_id, username["userName"])

        redis_key = f"room_id_players:{join_room.room_id}"
        initial_arr_length = redis_init.execute_command(
            RedisOperations.JSON_ARRAY_LENGTH.value, redis_key, ".members"
        )
        latest_player_id = int((redis_init.execute_command(RedisOperations.JSON_GET.value, redis_key, '.members[-1].player_id')).decode("utf-8"))
        logger.info(f"Latest player id: {latest_player_id}")

        redis_init.execute_command(
            RedisOperations.JSON_ARRAY_APPEND.value,
            redis_key,
            ".members",
            json.dumps({"player_id":latest_player_id+1, "is_active": True, "player_name": join_room.player_name, "score": 0}),
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
            socket_link = generate_socket_link(join_room.room_id)
            return {'socket-link': socket_link, 'success': True}
        else:
            logger.error(
                f"Error updating room details in Redis for key {redis_key}"
            )
            raise JoinRoomException(
                msg=f"Error updating room details in Redis for key {redis_key}"
            )
    except Exception as e:
        logger.error(traceback.format_exc())
        return {'success': False}
