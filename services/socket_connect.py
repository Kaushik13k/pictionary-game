import json
import logging
import traceback

from init.redis_init import redis_init
from services.socket_event import SocketEvent

from enums.redis_operations import RedisOperations
from enums.socket_operations import SocketOperations
import asyncio

from services.words_assignment import assign_words


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GUESS_TIME = 5


class Connect(SocketEvent):
    async def handle(self, sio: str, socket_id: str, message: str):
        try:
            await sio.emit(
                SocketOperations.CONNECT.value,
                {"sid": socket_id},
                room=socket_id,
            )
        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())
            await sio.emit(
                SocketOperations.CONNECT.value,
                {"error": "Failed to connect"},
                room=socket_id,
            )
