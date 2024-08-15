import json
import logging

from templates.socket_events import SocketEvent

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
