import json
import logging

from init.redis_init import redis_init
from models.players import PlayersModel
from templates.socket_events import SocketEvent
from utils.words_assignment import assign_words
from enums.redis_operations import RedisOperations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StartGame(SocketEvent):
    async def handle(self, message, manager, words_assign=True, current_round=1):
        try:
            logger.info(f"The Game is started!...")
            room_id = json.loads(message)["message"]["room_id"]
            redis_key = f"room_id_players:{room_id}"
            game_key = f"room_id_game:{room_id}"

            game = await self.get_game_data(game_key, manager)
            user = self.get_user_data(redis_key)

            players = user["members"]
            logger.info(f"Players: {players}")
            if current_round <= 3 * len(players):
                if words_assign:
                    words = await assign_words(
                        num_rounds=3, num_players=len(players), words_per_round=2
                    )

                    logger.info(f"Words assigned: {words}")
                    logger.info(f"Players: {players}")

                    for i, values in words.items():
                        print(f"values: {values}, i: {i}")
                        latest_player_id = redis_init.execute_command(
                            "JSON.SET",
                            redis_key,
                            f"$.members[{i-1}].words",
                            json.dumps(values),
                        )

                user = self.get_user_data(redis_key)
                players = user["members"]
                game["word_list"] = players
                result_game = redis_init.execute_command(
                    RedisOperations.JSON_SET.value, game_key, "$", json.dumps(game)
                )
                drawer = players[0]
                logger.info(f"drawer: {drawer}")
                await manager.send_personal_message(
                    {
                        "event": "select_word",
                        "value": drawer["words"][current_round - 1],
                    },
                    drawer["sid"],
                )

                await manager.broadcast(
                    {
                        "event": "choosing_word",
                        "value": f"{drawer['player_name']} is choosing.",
                    },
                    drawer["sid"],
                )
            else:
                await manager.broadcast(
                    {"event": "end_game", "value": f"Game endded!"},
                )
        except Exception as e:
            logger.error(e)

    async def get_game_data(self, game_key, manager):
        game = redis_init.execute_command(RedisOperations.JSON_GET.value, game_key)
        logger.info(f"Game data: {game}")
        if game is None:
            game = {}
            if game.get("rounds") is None:
                game["score_details"] = []
                game["rounds"] = 1
            await manager.broadcast(
                {"event": "round_begin", "value": f"Round {game['rounds']} Starts."}
            )
            self.set_game_data(game_key, game)
        else:
            game = json.loads(game)
            if game["turns"] == 0:
                await manager.broadcast(
                    {
                        "event": "round_begin",
                        "value": f"Round {game['rounds']} Starts.",
                    }
                )
        return game

    def set_game_data(self, game_key, game):
        result_game = redis_init.execute_command(
            RedisOperations.JSON_SET.value, game_key, "$", json.dumps(game)
        )

    def get_user_data(self, redis_key):
        user = json.loads(
            redis_init.execute_command(RedisOperations.JSON_GET.value, redis_key)
        )
        logger.info(f"User data: {user}")
        return user

    def set_user_data(self, redis_key, user):
        result_players = redis_init.execute_command(
            RedisOperations.JSON_SET.value, redis_key, "$", json.dumps(user)
        )
        logger.info(f"Set data in Redis for key {redis_key}")

    async def end_round(self, game, game_key, redis_key, manager):

        await manager.broadcast(
            {"event": "round_end", "value": f"Round {game['rounds']} ends."}
        )

        redis_init.execute_command(
            RedisOperations.JSON_NUMBER_INCR_BY.value, game_key, "$.rounds", 1
        )
        result_game = redis_init.execute_command(
            RedisOperations.JSON_SET.value, game_key, "$.turns", 0
        )
