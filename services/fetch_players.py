import json
import logging
import traceback
from fastapi import APIRouter

from templates.room_events import RoomEvents
from utils.api_response import success, error
from redis_json.redis_operations import RedisJson
from exceptions.exceptions import FetchPlayersException

from enums.redis_locations import RedisLocations
from enums.messages import EventSuccessMessages, EventFailedMessages


router = APIRouter()
logger = logging.getLogger(__name__)


class FetchPlayers(RoomEvents):
    async def handle_room(self):
        try:
            logger.info(f"Fetching the players for the room {self.room_data.room_id}.")
            redis_key = f"room_id_players:{self.room_data.room_id}"

            players = RedisJson().get(
                redis_key=redis_key, location=RedisLocations.MEMBERS.value
            )
            if not players:
                raise FetchPlayersException("wrong room id provided.")

            sorted_players = sorted(
                json.loads(players), key=lambda player: player["score"], reverse=True
            )

            return success(
                sorted_players, message=EventSuccessMessages.GET_PLAYER_SUCCESS.value
            )
        except Exception as e:
            logger.error(f"There was error fetching players")
            logger.error(e)
            logger.error(traceback.format_exc())
            return error(EventFailedMessages.GET_PLAYER_FAILED.value)
