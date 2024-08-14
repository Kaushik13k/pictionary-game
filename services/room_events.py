import uuid
from datetime import datetime
from pydantic import BaseModel
from abc import ABC, abstractmethod

from utils.get_room_ids import get_room_ids


class RoomEvents(ABC):
    def __init__(self, room_data: BaseModel):
        self.room_data = room_data

    @abstractmethod
    def handle_room(self):
        pass

    def generate_unique_room_id(self):
        while True:
            room_id = str(uuid.uuid4()) + "-" + str(int((datetime.now()).timestamp()))
            return room_id
