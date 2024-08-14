import logging
import traceback
from fastapi import APIRouter

from templates.room_events import RoomEvents
from utils.get_room_ids import get_room_ids
from utils.api_response import success, error


router = APIRouter()
logger = logging.getLogger(__name__)


class FetchRooms(RoomEvents):
    async def handle_room(self):
        try:
            logger.info("Fetching rooms..")
            rooms = get_room_ids()
            return success(rooms, message="Rooms fetched successfully")
        except Exception as e:
            logger.error(f"There was error fetching rooms: {e}")
            logger.info(traceback.format_exc())
            return error("Failed to fetch rooms")
