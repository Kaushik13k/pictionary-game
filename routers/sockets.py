from services.create_room import CreateRoom
from services.join_room import JoinRoom
from services.health import Health
from init.socket_init import socket_io


class SocketEventDispatcher:
    def __init__(self):
        self.events = {}

    def register_event(self, event_name: str, event: str):
        if event_name not in self.events:
            self.events[event_name] = event
        else:
            print(f"Event {event_name} is already registered.")

    async def dispatch_event(
        self, sio: str, event_name: str, socket_id: str, data: str
    ):
        event = self.events.get(event_name)
        if event is not None:
            await event.handle(sio, socket_id, data)


dispatcher = SocketEventDispatcher()
dispatcher.register_event("health", Health())
dispatcher.register_event("create_room", CreateRoom())
dispatcher.register_event("join_room", JoinRoom())


@socket_io.on("health")
async def health(socket_id: str, data: str):
    await dispatcher.dispatch_event(socket_io, "health", socket_id, data)


@socket_io.on("create_room")
async def create_room(socket_id: str, username: str):
    await dispatcher.dispatch_event(socket_io, "create_room", socket_id, username)


@socket_io.on("join_room")
async def join_room(socket_id: str, room: str):
    await dispatcher.dispatch_event(socket_io, "join_room", socket_id, room)


def create_socket():
    return socket_io
