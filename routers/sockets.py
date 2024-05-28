import logging


from services.health import Health
from init.socket_init import socket_io
from services.join_room import JoinRoom
from services.create_room import CreateRoom
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
        self, sio: str, event_name: str, socket_id: str, data: str
    ):
        logger.info(
            f"Dispatching event {event_name} for socket {socket_id} with data {data}"
        )
        event = self.events.get(event_name)
        if event is not None:
            await event.handle(sio, socket_id, data)


dispatcher = SocketEventDispatcher()
dispatcher.register_event(SocketOperations.HEALTH.value, Health())
dispatcher.register_event(SocketOperations.CREATE.value, CreateRoom())
dispatcher.register_event(SocketOperations.JOIN.value, JoinRoom())


@socket_io.on(SocketOperations.HEALTH.value)
async def health(socket_id: str, data: str):
    await dispatcher.dispatch_event(
        socket_io, SocketOperations.HEALTH.value, socket_id, data
    )


@socket_io.on(SocketOperations.CREATE.value)
async def create_room(socket_id: str, username: str):
    await dispatcher.dispatch_event(
        socket_io, SocketOperations.CREATE.value, socket_id, username
    )


@socket_io.on(SocketOperations.JOIN.value)
async def join_room(socket_id: str, room: str):
    await dispatcher.dispatch_event(
        socket_io, SocketOperations.JOIN.value, socket_id, room
    )


def create_socket():
    return socket_io
