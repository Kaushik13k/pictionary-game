from pydantic import BaseModel


class FetchPlayersModel(BaseModel):
    room_id: str
