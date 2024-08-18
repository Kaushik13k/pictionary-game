import logging
from typing import Dict, Optional
from starlette.websockets import WebSocket

from services.chat_room import ChatRoom
from services.start_game import StartGame
from services.selected_word import SelectedWord
from services.drawing_canvas import DrawingCanvas

from enums.socket_operations import SocketOperations

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(lineno)d",
)
logger = logging.getLogger(__name__)


class ConcreteStartGame(StartGame):
    async def execute(self, *args, **kwargs):
        pass


class ConcreteSelectedWord(SelectedWord):
    async def execute(self, *args, **kwargs):
        pass


class ConcreteDrawingCanvas(DrawingCanvas):
    async def execute(self, *args, **kwargs):
        pass


class ConcreteChatRoom(ChatRoom):
    async def execute(self, *args, **kwargs):
        pass


class ConnectionManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConnectionManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = {
            "socket_instance": websocket,
            "connected": False,
        }

        await websocket.send_json(
            {"event": SocketOperations.CONNECT.value, "value": client_id}
        )

    async def activate_connection(self, client_id: str):
        self.active_connections[client_id]["connected"] = True

    async def disconnect(self, client_id: str):
        del self.active_connections[client_id]
        await self.broadcast(
            {
                "event": SocketOperations.DISCONNECT.value,
                "value": f"Client #{client_id} left the chat.",
            },
            client_id,
        )

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def health(self, websocket: WebSocket, message: str):
        await websocket.send_json(
            {"event": "health", "value": "Health check successful"}
        )

    async def start_game(self, websocket: WebSocket, message: str, manager):
        start_game_instance = ConcreteStartGame()
        await start_game_instance.handle(
            message, manager, is_words_assign=True, current_turn=1, current_round=1
        )

    async def selected_word(self, websocket: WebSocket, message: str, manager):
        selected_word_instance = ConcreteSelectedWord()
        await selected_word_instance.handle(message, manager)

    async def drawing_canvas(self, websocket: WebSocket, message: str, manager):
        selected_word_instance = ConcreteDrawingCanvas()
        await selected_word_instance.handle(message, manager)

    async def chat_room(self, websocket: WebSocket, message: str, manager):
        selected_word_instance = ConcreteChatRoom()
        await selected_word_instance.handle(message, manager)

    async def send_personal_message(self, message: str, client_id: str):
        logger.info(f"Sending message to {client_id}")
        logger.info(f"Active connections: {self.active_connections}")
        await self.active_connections[client_id]["socket_instance"].send_json(message)

    async def broadcast(self, message: str, exclude: Optional[str] = None):
        for client_id, connection in self.active_connections.items():
            if client_id != exclude and connection["connected"]:
                await connection["socket_instance"].send_json(message)
