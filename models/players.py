from typing import Optional, List
from pydantic import BaseModel


# class PlayersModel(BaseModel):
#     player_id: int
#     is_active: bool
#     player_name: str
#     score: int
#     is_creator: bool
#     sid: str
#     words: Optional[list]


class Word(BaseModel):
    id: int
    word: str
    description: str


class PlayersModel(BaseModel):
    player_id: int
    is_active: bool
    player_name: str
    score: int
    is_creator: bool
    sid: str
    words: Optional[List[List[Word]]] = None


class Room(BaseModel):
    players: List[PlayersModel]
