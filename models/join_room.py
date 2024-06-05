from pydantic import BaseModel


class JoinRoomModel(BaseModel):
    sid: str
    player_name: str
    room_id: str
