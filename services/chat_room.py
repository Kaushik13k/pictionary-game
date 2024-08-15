import json
import logging

from init.redis_init import redis_init
from services.timer import TimerManager
from services.end_turn import end_turn
from templates.socket_events import SocketEvent
from enums.redis_operations import RedisOperations


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatRoom(SocketEvent):
    def set_game_data(self, game_key, game):
        result_game = redis_init.execute_command(
            RedisOperations.JSON_SET.value, game_key, "$", json.dumps(game)
        )

    async def handle(self, message, manager):
        try:
            logger.info(f"inside the chat_room!: {message}")
            message = json.loads(message)["message"]
            game_key = f"room_id_game:{message['room_id']}"
            redis_key = f"room_id_players:{message['room_id']}"

            result_game = json.loads(
                redis_init.execute_command(RedisOperations.JSON_GET.value, game_key)
            )
            players = json.loads(
                redis_init.execute_command(
                    RedisOperations.JSON_GET.value,
                    redis_key,
                    ".members",
                )
            )
            logger.info(f"the result_game is: {result_game}")
            selected_word = result_game["selected_word"]
            logger.info(f"the selected word is: {selected_word}")
            res = list(filter(lambda player: player["sid"] == message["sid"], players))
            logger.info(f"the res is: {res}")
            if res:
                player_item, *rest = res
                logger.info(f'the res name is: {player_item.get("player_name")}')

                if message["word"].lower() == selected_word:
                    logger.info("the word matched!")

                    await manager.send_personal_message(
                        {"event": "guessed", "value": "You have guessed the word"},
                        message["sid"],
                    )

                    await manager.broadcast(
                        {
                            "event": "word_guessed",
                            "value": f"{player_item.get('player_name')} has guessed the word",
                        },
                        message["sid"],
                    )

                    game_score_details = {
                        "sid": message["sid"],
                        "time_elapsed": message["time_elapsed"],
                        "position": len(result_game["score_details"]) + 1,
                    }
                    result_game["score_details"].append(game_score_details)
                    self.set_game_data(game_key, result_game)
                    if len(result_game["score_details"]) == len(players) - 1:
                        TimerManager.instance().stop_timer(message["room_id"])
                        logger.info(
                            f"message: Timer for Game {message['room_id']} stopped"
                        )
                        await end_turn(message["room_id"], manager, is_time_up=False)

                else:
                    logger.info("the word didnot match. Hence broadcasting!")
                    await manager.broadcast(
                        {
                            "event": "chat_room",
                            "value": {
                                "word": message["word"],
                                "player_name": player_item.get("player_name"),
                            },
                        },
                        message["sid"],
                    )

        except Exception as e:
            logger.info("ERROR!")
