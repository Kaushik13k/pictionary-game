from enum import Enum


class EventSuccessMessages(Enum):
    ROOM_CREATION_SUCCESS = "Room created successfully"
    ROOM_JOIN_SUCCESS = "Joined the room"


class EventFailedMessages(Enum):
    ROOM_CREATION_FAILED = "Room creation failed"
    ROOM_JOIN_FAILED = "Room join failed"
