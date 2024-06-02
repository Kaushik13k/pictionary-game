import logging
from fastapi import APIRouter

from services.create_room import CreateRoom
from models.create_room import CreateRoomModel


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/create-room", tags=["Heath"], responses={404: {"description": "Not found"}}
)
async def create_room(room: CreateRoomModel):
    room_factory = CreateRoom(room)
    return await room_factory.handle_room()
