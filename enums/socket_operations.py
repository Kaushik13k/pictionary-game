from enum import Enum


class SocketOperations(Enum):
    CONNECT = "connect"
    DISCONNECT = "disconnect"

    HEALTH = "health"
    CREATE = "create_room"
    JOIN = "join_room"
    LEAVE = "leave_room"

    START_GAME = "start_game"
    SELECTED_WORD = "selected_word"
    CANVAS = "drawing_canvas"
    CHAT_ROOM = "chat_room"
    END_GAME = "end_game"

    START_TURN = "start_turn"
    END_TURN = "end_turn"

    START_ROUND = "start_round"
    END_ROUND = "end_round"
