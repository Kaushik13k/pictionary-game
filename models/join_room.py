from pydantic import BaseModel


class JoinRoomModel(BaseModel):
    player_name: str
    room_id: str
