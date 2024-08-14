import logging
from fastapi import APIRouter

from services.fetch_game import FetchGames
from models.fetch_game import FetchGamesModel

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/fetch-game-info",
    tags=["Fetch Game info"],
    responses={404: {"description": "Not found"}},
)
async def fetch_game(room: FetchGamesModel):
    game_factory = FetchGames(room)
    return await game_factory.handle_room()
