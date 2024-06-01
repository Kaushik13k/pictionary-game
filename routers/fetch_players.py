import logging
from fastapi import APIRouter

from models.fetch_players import FetchPlayersModel
from services.fetch_players import FetchPlayers

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/fetch-players", tags=["Heath"], responses={404: {"description": "Not found"}}
)
async def fetch_room(room: FetchPlayersModel):
    room_factory = FetchPlayers(room)
    return await room_factory.handle_room()
