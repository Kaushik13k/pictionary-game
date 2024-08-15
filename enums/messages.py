from enum import Enum


class EventSuccessMessages(Enum):
    ROOM_CREATION_SUCCESS = "Room created successfully."
    ROOM_JOIN_SUCCESS = "Joined the room."

    GET_PLAYER_SUCCESS = "Players fetched successfully."
    GET_GAME_SUCCESS = "Game details fetched."
    GET_ROOMS_SUCCESS = "Rooms fetched successfully."

    CHATROOM_WORD_GUESSED = "You have guessed the word."


class EventFailedMessages(Enum):
    ROOM_CREATION_FAILED = "Room creation failed."
    ROOM_JOIN_FAILED = "Room join failed."
    GET_PLAYER_FAILED = "Failed to fetch players."
    GET_GAME_FAILED = "Failed to fetch game details."
    GET_ROOMS_FAILED = "Failed to fetch rooms"
