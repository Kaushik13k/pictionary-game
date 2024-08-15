import json
import logging
from typing import List
from pydantic import BaseModel

from init.redis_init import redis_init
from services.timer import TimerManager
from templates.socket_events import SocketEvent
from enums.redis_operations import RedisOperations


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
                redis_init.execute_command(RedisOperations.JSON_GET.value, game_key)
            )

            logger.info(f"the list of words is: {result_game}")
            players_word_list = result_game["word_list"]
            logger.info(f"players_word_list {players_word_list}")

            room = Room(
                players=[Player(**player_group) for player_group in players_word_list]
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
                result_game["selected_word"] = word.word
                logger.info(f"the result is---{result_game}")
                result_game_resut = redis_init.execute_command(
                    RedisOperations.JSON_SET.value,
                    game_key,
                    "$",
                    json.dumps(result_game),
                )

                await manager.broadcast(
                    {
                        "event": "word_choosen",
                        "value": {
                            "word_length": len(word.word),
                            "value": f"{'_ ' * len(word.word)}",
                        },
                    },
                    message["sid"],
                )
                TimerManager.instance().start_timer(message["room_id"], 15, manager)
                # TODO: Start timer for 60 seconds
                logger.info(
                    f"message: Timer for Game {message['room_id']} started for 60 seconds"
                )

            else:
                logger.info("Word not found")
            result_game = json.loads(
                redis_init.execute_command(RedisOperations.JSON_GET.value, game_key)
            )
            logger.info(f"the list of words is: {result_game}")

        except Exception as e:
            logger.info("ERROR!")
