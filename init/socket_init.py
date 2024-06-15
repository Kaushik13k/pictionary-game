import socketio

socket_io = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    allow_origins=["*"],
    ping_timeout=120,
    ping_interval=115,
)
