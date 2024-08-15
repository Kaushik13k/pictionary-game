class CreateRoomException(Exception):
    def __init__(self, msg: str = None):
        super().__init__(msg)


class JoinRoomException(Exception):
    def __init__(self, msg: str = None):
        super().__init__(msg)


class FetchPlayersException(Exception):
    def __init__(self, msg: str = None):
        super().__init__(msg)
    
class FetchGameException(Exception):
    def __init__(self, msg: str = None):
        super().__init__(msg)

class ChatRoomException(Exception):
    def __init__(self, msg: str = None):
        super().__init__(msg)
