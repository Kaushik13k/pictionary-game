from enum import Enum

class SocketOperations(Enum):
    HEALTH = "health"
    CREATE = "create_room"
    JOIN = "join_room"
    LEAVE = "leave_room"

    START_GAME = "start_game"
    END_GAME = "end_game"

    START_TURN = "start_turn"
    END_TURN = "end_turn"

    START_ROUND = "start_round"
    END_ROUND = "end_round"
    
