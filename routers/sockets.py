from services.create_room import CreateRoom
from init.socket_init import socket_io


class SocketEventDispatcher:
    def __init__(self):
        self.events = {}

    def register_event(self, event_name, event):
        self.events[event_name] = event

    async def dispatch_event(self, sio, event_name, sid, data):
        event = self.events.get(event_name)
        if event is not None:
            await event.handle(sio, sid, data)

dispatcher = SocketEventDispatcher()
dispatcher.register_event('create_room', CreateRoom())

@socket_io.on('create_room')
async def create_room(sid, username):
    await dispatcher.dispatch_event(socket_io, 'create_room', sid, username)

def create_sio():
    return socket_io
