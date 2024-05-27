import socketio

socket_io = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins="*",
    allow_origins=["*"]
)