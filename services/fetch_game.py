import json
import logging
import traceback
from fastapi import APIRouter

from enums.redis_operations import RedisOperations
from exceptions.exceptions import FetchPlayersException
from init.redis_init import redis_init
from templates.room_events import RoomEvents
from utils.api_response import success, error


router = APIRouter()
logger = logging.getLogger(__name__)


class FetchGames(RoomEvents):
    async def handle_room(self):
        try:
            logger.info(
                f"Fetching the Game Details for the room {self.room_data.room_id}.."
            )
            redis_key = f"room_id_game:{self.room_data.room_id}"
            players = redis_init.execute_command(
                RedisOperations.JSON_GET.value, redis_key
            )
            if not players:
                raise FetchPlayersException("wrong room id provided.")
            logger.info(f"Players fetched successfully for the room {players}")
            players = json.loads(players)
            return success(players, message="Players fetched successfully")
        except Exception as e:
            logger.error(f"There was error fetching players: {e}")
            logger.info(traceback.format_exc())
            return error("Failed to fetch players. Check the room id provided.")
