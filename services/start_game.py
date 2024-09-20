import json
import asyncio
import logging
import traceback

from init.redis_init import redis_init
from services.socket_event import SocketEvent
from enums.redis_operations import RedisOperations
from services.words_assignment import assign_words
from models.players import PlayersModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GUESS_TIME = 40
SELECTION_TIME = 30

GUESSER_GUESS_MAX_POINTS = 400
GUESSER_TIME_MAX_POINTS = 200

DRAWER_GUESS_MAX_POINTS = 300
DRAWER_TIME_MAX_POINTS = 100


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

    async def calculate_drawer_scores(self, players_guessed, total_time, total_players):
        logger.info(
            f"the total players is {total_players + 1}, the calc total players is {total_players}"
        )
        logger.info(f"the total time is {total_time}")
        logger.info(f"the players guessed is {players_guessed}")
        guessing_score = 0
        # Guessing points
        if players_guessed == total_players:
            guessing_score = DRAWER_GUESS_MAX_POINTS
        else:
            guessing_score = (players_guessed / total_players) * DRAWER_GUESS_MAX_POINTS

        # Timing points
        timing_score = (
            GUESS_TIME / total_time * DRAWER_TIME_MAX_POINTS if total_time > 0 else 0
        )

        final_score = guessing_score + timing_score
        return final_score

    async def calculate_guesser_scores(self, game_key, redis_key, drawer):
        logger.info("Calculating the score...")

        # Retrieve player score details from Redis
        player_score_details = json.loads(
            redis_init.execute_command(
                RedisOperations.JSON_GET.value,
                game_key,
            )
        )
        logger.info(f"the player_score_details list is: {player_score_details}")

        # Retrieve players from Redis
        players = json.loads(
            redis_init.execute_command(
                RedisOperations.JSON_GET.value,
                redis_key,
                ".members",
            )
        )
        logger.info(f"the player list is: {players}")

        # Create player models
        players_model = [PlayersModel(**player) for player in players]

        # Calculate scores
        total_time = 0
        players_guessed = len(player_score_details["score_details"])
        total_players = len(players) - 1
        drawer_calculation = True
        for player in player_score_details["score_details"]:
            total_time = total_time + player["time_elapsed"]

        drawer_score = await self.calculate_drawer_scores(
            players_guessed, total_time, total_players
        )
        logger.info(f"the score for the drawer is: {drawer_score}")

        # Update score in players_model if player_id matches
        for p_model in players_model:
            logger.info(
                f"the model sid is, type is: {p_model.sid, type(p_model.sid)} and dict sid, type is: {drawer['sid'], type(drawer['sid'])}"
            )
            if str(p_model.sid) == drawer["sid"]:
                logger.info(f"updating the score: {int(drawer_score)}")
                p_model.score = p_model.score + int(drawer_score)

        for player in player_score_details["score_details"]:
            position = player["position"]
            time_elapsed = player["time_elapsed"]
            percentage = max(10, 90 - (position - 1) * 10)
            guess_score = (percentage / 100) * GUESSER_GUESS_MAX_POINTS

            time_score = (
                (time_elapsed / GUESS_TIME) * GUESSER_TIME_MAX_POINTS
                if time_elapsed != 0
                else GUESSER_TIME_MAX_POINTS
            )
            total_score = int(guess_score + time_score)
            player["score"] = total_score

            # Update score in players_model if player_id matches
            for p_model in players_model:
                logger.info(
                    f"the model sid is, type is: {p_model.sid, type(p_model.sid)} and dict sid, type is: {player['sid'], type(player['sid'])}"
                )
                if str(p_model.sid) == player["sid"]:
                    logger.info(f"updating the score: {total_score}")
                    p_model.score = p_model.score + total_score

        logger.info(
            f"the updated score details of the player is: {player_score_details}"
        )

        # Optionally log the updated players_model
        for i in players_model:
            logger.info(
                f"the player id from players_model is {i.player_id} with updated score {i.score}"
            )

        players_json = [player.dict() for player in players_model]
        logger.info(f"the final players json is: {players_json}")
        logger.info(f"Redis Key: {redis_key}")

        result_game = redis_init.execute_command(
            RedisOperations.JSON_SET.value,
            redis_key,
            ".members",
            json.dumps(players_json),
        )

        logger.info(f"Result of JSON.SET command: {result_game}")

        retrieved_value = self.get_user_data(redis_key)
        logger.info(f"Retrieved Value: {retrieved_value}")
        return retrieved_value

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
