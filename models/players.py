from typing import Optional
from pydantic import BaseModel


class PlayersModel(BaseModel):
    player_id: int
    is_active: bool
    player_name: str
    score: int
    is_creator: bool
    sid: str
    words: Optional[list]
