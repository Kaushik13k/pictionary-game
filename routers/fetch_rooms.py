import logging
from fastapi import Header
from fastapi import APIRouter

from models.fetch_rooms import FetchRoomsModel
from services.fetch_rooms import FetchRooms


router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get("/fetch-rooms", tags=["Rooms"], responses={404: {"description": "Not found"}})
async def create_room(user_id: str = Header(None)):
    room_factory = FetchRooms(user_id)
    return await room_factory.handle_room()
