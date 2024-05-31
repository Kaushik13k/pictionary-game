import logging
import uvicorn

from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from starlette.routing import Match
import socketio

from routers import create_room, get_rooms, join_room, health, sockets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    logger.info("Started the server!")
    yield
    # shutdown
    logger.info("Shutdown the server!")


app = FastAPI(
    title="Pictionary Game",
    version="0.0.1",
    contact={"name": "Kaushik", "email": "13kaushikk@gmail.com"},
    debug=True,
    lifespan=lifespan,
)

socket_io = sockets.create_socket()


@app.middleware("https")
async def log_middlewear(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    routes = request.app.router.routes
    logger.info("Params: ")
    for route in routes:
        match, scope = route.matches(request)
        if match == Match.FULL:
            for name, value in scope["path_params"].items():
                logger.info(f"{name}: {value}")
    logger.info("Headers: ")
    for name, value in request.headers.items():
        logger.info(f"{name}: {value}")

    response = await call_next(request)
    logger.info(f"{request.method} {request.url} {response.status_code}")
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/v1")
app.include_router(create_room.router, prefix="/v1")
app.include_router(join_room.router, prefix="/v1")
app.include_router(get_rooms.router, prefix="/v1")
app.mount("/", socketio.ASGIApp(socket_io))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
