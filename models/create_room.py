from pydantic import BaseModel


class CreateRoomModel(BaseModel):
    rounds: int
    time: int
    player_name: str
    max_players_count: int
    hints: int
    word_count: int
