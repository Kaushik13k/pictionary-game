import json
import logging
import traceback
from fastapi import APIRouter

from init.redis_init import redis_init
from templates.room_events import RoomEvents
from utils.api_response import success, error
from exceptions.exceptions import FetchGameException
from redis_json.redis_operations import RedisJson

from enums.redis_locations import RedisLocations
from enums.redis_operations import RedisOperations
from enums.messages import EventFailedMessages, EventSuccessMessages


router = APIRouter()
logger = logging.getLogger(__name__)


class FetchGames(RoomEvents):
    async def handle_room(self):
        try:
            logger.info(
                f"Fetching the Game Details for the room {self.room_data.room_id}."
            )
            redis_key = f"room_id_game:{self.room_data.room_id}"
            game_details = redis_init.execute_command(
                RedisOperations.JSON_GET.value, redis_key
            )

            if not game_details:
                raise FetchGameException("Wrong room id provided.")

            return success(
                json.loads(game_details),
                message=EventSuccessMessages.GET_GAME_SUCCESS.value,
            )
        except Exception as e:
            logger.error(f"There was error fetching game details.")
            logger.error(e)
            logger.error(traceback.format_exc())
            return error(EventFailedMessages.GET_GAME_FAILED.value)
