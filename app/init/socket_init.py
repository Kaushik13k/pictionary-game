import socketio

socket_io = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins="*",
    allow_origins=["*"],
    max_http_buffer_size=1000000,
    ping_interval=25000,
    ping_timeout=20000
)