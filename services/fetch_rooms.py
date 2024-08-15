import logging
import traceback
from fastapi import APIRouter

from utils.get_room_ids import get_room_ids
from templates.room_events import RoomEvents
from utils.api_response import success, error
from enums.messages import EventFailedMessages, EventSuccessMessages


router = APIRouter()
logger = logging.getLogger(__name__)


class FetchRooms(RoomEvents):
    async def handle_room(self):
        try:
            logger.info("Fetching rooms..")
            rooms = get_room_ids()
            return success(rooms, message=EventSuccessMessages.GET_ROOMS_SUCCESS.value)
        except Exception as e:
            logger.error(f"There was error fetching rooms")
            logger.error(e)
            logger.info(traceback.format_exc())
            return error(EventFailedMessages.GET_ROOMS_FAILED.value)
