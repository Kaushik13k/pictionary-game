import logging

from init.socket_init import socket_io
from services.socket_health import Health
from services.start_game import StartGame
from services.socket_connect import Connect
from enums.socket_operations import SocketOperations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SocketEventDispatcher:
    def __init__(self):
        self.events = {}

    def register_event(self, event_name: str, event: str):
        if event_name not in self.events:
            self.events[event_name] = event
            logger.info(f"Event {event_name} registered.")
        else:
            logger.warning(f"Event {event_name} is already registered.")

    async def dispatch_event(
        self, sio: str, event_name: str, socket_id: str, message: str
    ):
        logger.info(
            f"Dispatching event {event_name} for socket {socket_id} with data {message}"
        )
        event = self.events.get(event_name)
        if event is not None:
            await event.handle(sio, socket_id, message)


dispatcher = SocketEventDispatcher()
dispatcher.register_event(SocketOperations.HEALTH.value, Health())
dispatcher.register_event(SocketOperations.CONNECT.value, Connect())
dispatcher.register_event(SocketOperations.START_GAME.value, StartGame())


@socket_io.on(
    SocketOperations.CONNECT.value,
)
async def connect(socket_id, message):
    await dispatcher.dispatch_event(
        socket_io, SocketOperations.CONNECT.value, socket_id, message
    )
    # await sio.emit("connect", {"sid": sid}, room=sid)


# @socket_io.on(SocketOperations.DISCONNECT.value)
# async def disconnect(socket_id, message):
#     await dispatcher.dispatch_event(
#         socket_io, SocketOperations.DISCONNECT.value, socket_id, message
#     )


@socket_io.on(SocketOperations.HEALTH.value)
async def health(socket_id: str, message: str):
    await dispatcher.dispatch_event(
        socket_io, SocketOperations.HEALTH.value, socket_id, message
    )


@socket_io.on(SocketOperations.START_GAME.value)
async def start_game(socket_id: str, message: str):
    await dispatcher.dispatch_event(
        socket_io, SocketOperations.START_GAME.value, socket_id, message
    )


def create_socket():
    return socket_io
