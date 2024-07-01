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


class ChatRoom(SocketEvent):
    async def handle(self, message, manager):
        try:
            logger.info(f"inside the chat_room!: {message}")
            message = json.loads(message)["message"]
            game_key = f"room_id_game:{message['room_id']}"
            result_game = json.loads(
                redis_init.execute_command(RedisOperations.JSON_GET.value, game_key)
            )
            logger.info(f"the result_game is: {result_game}")
            selected_word = result_game["selected_word"]
            logger.info(f"the selected word is: {selected_word}")

            if message["word"] == selected_word:
                logger.info("the word matched!")
                await manager.send_personal_message(
                    {"event": "guessed", "value": "You have guessed the word"},
                    message["sid"],
                )

                await manager.broadcast(
                    {
                        "event": "word_guessed",
                        "value": "{message['sid']} has guessed the word",
                    },
                    message["sid"],
                )
            else:
                logger.info("the word didnot match. Hence broadcasting!")
                await manager.broadcast(
                    {
                        "event": "chat_room",
                        "value": message["word"],
                    },
                    message["sid"],
                )

        except Exception as e:
            logger.info("ERROR!")
