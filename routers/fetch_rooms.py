import logging
from fastapi import Header
from fastapi import APIRouter

from services.fetch_rooms import FetchRooms

router = APIRouter()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(lineno)d",
)
logger = logging.getLogger(__name__)


@router.get(
    "/fetch-rooms", tags=["Fetch Rooms"], responses={404: {"description": "Not found"}}
)
async def create_room(user_id: str = Header(None)):
    room_factory = FetchRooms(user_id)
    return await room_factory.handle_room()
