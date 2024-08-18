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

    WORD_TO_SELECT = "select_word"
    CHOOSING_WORD = "choosing_word"
    WORD_CHOOSEN = "word_choosen"
    END_GAME = "end_game"

    ROUND_BEGIN = "round_begin"

    WORD_GUESSED_BROADCAST = "word_guessed"
    WORD_GUESSED_PERSONAL = "guessed"
