from pydantic import BaseModel


class FetchGamesModel(BaseModel):
    room_id: str
