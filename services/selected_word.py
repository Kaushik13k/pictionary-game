import json
import logging
import traceback

from utils.timer import TimerManager
from models.players import PlayersModel, Room
from templates.socket_events import SocketEvent
from redis_json.redis_operations import RedisJson
from exceptions.exceptions import SelectedWordException

from enums.redis_locations import RedisLocations
from enums.socket_operations import SocketOperations


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(lineno)d",
)
logger = logging.getLogger(__name__)


class SelectedWord(SocketEvent):
    async def handle(self, message, manager):
        try:
            logger.info(f"Executing the Selected word: {message}")
            message = json.loads(message)["message"]
            game_key = f"room_id_game:{message['room_id']}"
            result_game = json.loads(
                RedisJson().get(redis_key=game_key, location=RedisLocations.NIL.value)
            )
            if not result_game:
                logger.error("Game not found")
                raise SelectedWordException("Game not found")

            room = Room(
                players=[
                    PlayersModel(**player_group)
                    for player_group in result_game["word_list"]
                ]
            )

            sid_to_player = {player.sid: player for player in room.players}

            word_id_to_word = {
                word.id: word
                for player in room.players
                for word_list in player.words
                for word in word_list
            }

            if (
                message["sid"] in sid_to_player
                and message["word_id"] in word_id_to_word
            ):
                word = word_id_to_word[message["word_id"]]

                result_game["selected_word"] = word.word
                logger.info(f"Selected word-1: {result_game}")

                result_game_resut = RedisJson().set(
                    redis_key=game_key, redis_value=result_game
                )
                if not result_game_resut:
                    logger.error("Error in setting selected word to redis.")
                    raise SelectedWordException(
                        "Error in setting selected word to redis."
                    )

                await manager.broadcast(
                    {
                        "event": SocketOperations.WORD_CHOOSEN.value,
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
                logger.info("Word not found.")

            result_game = json.loads(
                RedisJson().get(redis_key=game_key, location=RedisLocations.NIL.value)
            )
            if not result_game:
                logger.error("Game not found")
                raise SelectedWordException("Game not found")

        except Exception as e:
            logger.error(f"Error in SelectedWord")
            logger.error(e)
            logger.error(traceback.format_exc())
            return
