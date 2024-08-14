from enum import Enum


class EventSuccessMessages(Enum):
    ROOM_CREATION_SUCCESS = "Room created successfully"


class EventFailedMessages(Enum):
    ROOM_CREATION_FAILED = "Room creation failed"
