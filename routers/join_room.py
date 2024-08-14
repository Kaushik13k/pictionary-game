from fastapi import APIRouter

from services.join_room import JoinRoom
from models.join_room import JoinRoomModel

router = APIRouter()


@router.post(
    "/join-room", tags=["Join Room"], responses={404: {"description": "Not found"}}
)
async def join_room_endpoint(join_room: JoinRoomModel):
    room_factory = JoinRoom(join_room)
    return await room_factory.handle_room()
