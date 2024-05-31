import uuid
from pydantic import BaseModel
from abc import ABC, abstractmethod


class RoomEvents(ABC):
    def __init__(self, room_data: BaseModel):
        self.room_data = room_data

    @abstractmethod
    def handle_room(self):
        pass

    def generate_unique_room_id(self):
        return str(uuid.uuid4())

    def generate_socket_link(self, room_id):
        return f"ws://0.0.0.0:8000/{room_id}"
