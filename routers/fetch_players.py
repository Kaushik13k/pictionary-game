import logging
from fastapi import APIRouter

from services.fetch_players import FetchPlayers
from models.fetch_players import FetchPlayersModel

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/fetch-players",
    tags=["Fetch Players"],
    responses={404: {"description": "Not found"}},
)
async def fetch_room(room: FetchPlayersModel):
    room_factory = FetchPlayers(room)
    return await room_factory.handle_room()
