import json
import logging
import traceback

from templates.socket_events import SocketEvent
from utils.words_assignment import assign_words
from redis_json.redis_operations import RedisJson
from exceptions.exceptions import StartGameException

from enums.messages import EventSuccessMessages
from enums.redis_locations import RedisLocations
from enums.socket_operations import SocketOperations

from constants import constants

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(lineno)d",
)
logger = logging.getLogger(__name__)

# TODO: REMOVE HARD CODED VALUES
ROUNDS = 3


class StartGame(SocketEvent):
    async def handle(
        self, message, manager, is_words_assign=True, current_turn=1, current_round=1
    ):
        try:
            if current_round <= ROUNDS:
                logger.info(f"Start game is been called.")
                room_id = json.loads(message)["message"]["room_id"]
                redis_key = f"room_id_players:{room_id}"
                game_key = f"room_id_game:{room_id}"

                game = await self.get_game_data(game_key, manager)
                user = json.loads(
                    RedisJson().get(
                        redis_key=redis_key, location=RedisLocations.NIL.value
                    )
                )
                if not user:
                    logger.error("No user data found.")
                    raise StartGameException("No user data found.")

                players = user["members"]

                if is_words_assign:
                    words = await assign_words(
                        num_rounds=ROUNDS,
                        num_players=len(players),
                        words_per_round=constants.NO_OF_WORDS_SELECTION,
                    )

                    for id, values in words.items():
                        latest_player_id = RedisJson().set(
                            redis_key=redis_key,
                            redis_value=values,
                            location=f"$.members[{id-1}].words",
                        )
                        if not latest_player_id:
                            logger.error("Error in setting words.")
                            raise StartGameException("Error in setting words.")

                user = json.loads(
                    RedisJson().get(
                        redis_key=redis_key, location=RedisLocations.NIL.value
                    )
                )
                if not user:
                    logger.error("No user data found.")
                    raise StartGameException("No user data found.")

                players = user["members"]
                game["word_list"] = players
                result_game = RedisJson().set(redis_key=game_key, redis_value=game)
                logger.warning(f"the player list is = {players}")
                drawer = players[0]
                if not result_game:
                    raise StartGameException("Error in setting game data.")

                await manager.send_personal_message(
                    {
                        "event": SocketOperations.WORD_TO_SELECT.value,
                        "value": drawer["words"][current_round - 1],
                    },
                    drawer["sid"],
                )

                await manager.broadcast(
                    {
                        "event": SocketOperations.CHOOSING_WORD.value,
                        "value": f"{drawer['player_name']} is choosing.",
                    },
                    drawer["sid"],
                )
            else:
                await manager.broadcast(
                    {
                        "event": SocketOperations.END_GAME.value,
                        "value": EventSuccessMessages.END_GAME_SUCCESS.value,
                    },
                )
        except Exception as e:
            logger.error(f"Error in start game.")
            logger.error(e)
            logger.error(traceback.format_exc())
            return

    async def get_game_data(self, game_key, manager):
        logger.info("Setting the game data.")
        game = RedisJson().get(redis_key=game_key, location=RedisLocations.NIL.value)
        if game is None:
            logger.info("The game data is None.")
            game = {"score_details": [], "rounds": 1}
            await manager.broadcast(
                {
                    "event": SocketOperations.ROUND_BEGIN.value,
                    "value": f"Round {game['rounds']} Starts.",
                }
            )
            if not RedisJson().set(redis_key=game_key, redis_value=game):
                raise StartGameException(
                    "There was error in settting the data in redis."
                )
        else:
            logger.info("The game data is not None.")
            game = json.loads(game)
            if game["turns"] == 0:
                await manager.broadcast(
                    {
                        "event": SocketOperations.ROUND_BEGIN.value,
                        "value": f"Round {game['rounds']} Starts.",
                    }
                )
        return game
