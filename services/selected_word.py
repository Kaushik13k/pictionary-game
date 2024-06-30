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


class Word(BaseModel):
    id: int
    word: str
    description: str


class Player(BaseModel):
    player_id: int
    is_active: bool
    player_name: str
    score: int
    is_creator: bool
    sid: str
    words: List[List[Word]]


class Room(BaseModel):
    players: List[Player]


class SelectedWord(SocketEvent):
    async def handle(self, message, manager):
        try:
            logger.info(f"inside the selected wowrd!: {message}")
            message = json.loads(message)["message"]
            game_key = f"room_id_game:{message['room_id']}"
            result_game = json.loads(
                redis_init.execute_command(
                    RedisOperations.JSON_GET.value, game_key, "$.word_list"
                )
            )
            logger.info(f"the list of words is: {result_game}")

            room = Room(
                players=[
                    Player(**player)
                    for player_group in result_game
                    for player in player_group
                ]
            )

            sid_to_player = {player.sid: player for player in room.players}

            word_id_to_word = {
                word.id: word
                for player in room.players
                for word_list in player.words
                for word in word_list
            }

            sid_to_find = message["sid"]
            word_id_to_find = message["word_id"]

            if sid_to_find in sid_to_player and word_id_to_find in word_id_to_word:
                word = word_id_to_word[word_id_to_find]
                logger.info(
                    f"Word found: {word.word} with description: {word.description}"
                )
                game = {}
                game["selected_word"] = word.word
                result_game = redis_init.execute_command(
                    RedisOperations.JSON_SET.value, game_key, "$", json.dumps(game)
                )

                await manager.send_personal_message(
                    {
                        "event": "word_selected",
                        "value": word.word,
                    },
                    message["sid"],
                )
                await manager.broadcast(
                    {
                        "event": "word_choosen",
                        "value": {
                            "word_length": len(word.word),
                            "value": f"{'_' * len(word.word)}",
                        },
                    },
                    message["sid"],
                )

            else:
                logger.info("Word not found")
            result_game = json.loads(
                redis_init.execute_command(RedisOperations.JSON_GET.value, game_key)
            )
            logger.info(f"the list of words is: {result_game}")

        except Exception as e:
            logger.info("ERROR!")