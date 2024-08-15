import json
import logging
import traceback

from templates.socket_events import SocketEvent
from enums.socket_operations import SocketOperations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DrawingCanvas(SocketEvent):
    async def handle(self, message, manager):
        try:
            message = json.loads(message)["message"]
            await manager.broadcast(
                {
                    "event": SocketOperations.CANVAS.value,
                    "value": {"full_canvas_data": message["full_canvas_data"]},
                },
                message["sid"],
            )
        except Exception as e:
            logger.error(f"Error in DrawingCanvas")
            logger.error(e)
            logger.error(traceback.format_exc())
            return
