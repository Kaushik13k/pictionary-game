from services.create_room import CreateRoom
from services.join_room import JoinRoom
from init.socket_init import socket_io


class SocketEventDispatcher:
    def __init__(self):
        self.events = {}

    def register_event(self, event_name, event):
        if event_name not in self.events:
            self.events[event_name] = event
        else:
            print(f"Event {event_name} is already registered.")

    async def dispatch_event(self, sio, event_name, sid, data):
        event = self.events.get(event_name)
        if event is not None:
            await event.handle(sio, sid, data)

dispatcher = SocketEventDispatcher()
dispatcher.register_event('create_room', CreateRoom())
dispatcher.register_event('join_room', JoinRoom())


@socket_io.on('create_room')
async def create_room(sid, username):
    await dispatcher.dispatch_event(socket_io, 'create_room', sid, username)

@socket_io.on('join_room')
async def join_room(sid, room):
    await dispatcher.dispatch_event(socket_io, 'join_room', sid, room)


def create_sio():
    return socket_io
