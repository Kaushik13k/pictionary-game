from enum import Enum

class SocketOperations(Enum):
    HEALTH = "health"
    CREATE = "create_room"
    JOIN = "join_room"
    LEAVE = "leave_room"
    START = "start_game"
    
