import json
import asyncio
import logging
import traceback
from pydantic import BaseModel, Field
from typing import List, Dict, Union

from init.redis_init import redis_init
from services.socket_event import SocketEvent
from enums.redis_operations import RedisOperations
from services.words_assignment import assign_words


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DrawingCanvas(SocketEvent):
    async def handle(self, message, manager):
        try:
            message = json.loads(message)["message"]
            await manager.broadcast(
                {
                    "event": "drawing_canvas",
                    "value": {"full_canvas_data": message["full_canvas_data"]},
                },
                message["sid"],
            )
        except Exception as e:
            logger.info("ERROR!")
