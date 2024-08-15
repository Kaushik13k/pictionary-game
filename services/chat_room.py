import json
import logging
import traceback

from services.end_turn import end_turn
from utils.timer import TimerManager

from init.redis_init import redis_init
from templates.socket_events import SocketEvent
from redis_json.redis_operations import RedisJson
from exceptions.exceptions import ChatRoomException


from enums.messages import EventSuccessMessages
from enums.redis_locations import RedisLocations
from enums.redis_operations import RedisOperations
from enums.socket_operations import SocketOperations


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatRoom(SocketEvent):
    def set_game_data(self, game_key, game):
        game_result = redis_init.execute_command(
            RedisOperations.JSON_SET.value, game_key, "$", json.dumps(game)
        )

    async def handle(self, message, manager):
        try:
            logger.info(f"Handling chat room with message: {message}")
            message = json.loads(message)["message"]
            game_key = f"room_id_game:{message['room_id']}"
            redis_key = f"room_id_players:{message['room_id']}"

            game_result = json.loads(
                RedisJson().get(redis_key=game_key, location=RedisLocations.NIL.value)
            )
            if not game_result:
                raise ChatRoomException("The game result are not found in redis.")

            players = json.loads(
                RedisJson().get(
                    redis_key=redis_key, location=RedisLocations.MEMBERS.value
                )
            )
            if not players:
                raise ChatRoomException("The players are not found in redis.")

            selected_word = game_result["selected_word"]

            player_result = list(
                filter(lambda player: player["sid"] == message["sid"], players)
            )
            if not player_result:
                raise ChatRoomException("The players result is not found in redis.")

            player_item, *rest = player_result

            if message["word"].lower() == selected_word.lower():
                logger.info("The word is matched.")

                await manager.send_personal_message(
                    {
                        "event": SocketOperations.WORD_GUESSED_PERSONAL.value,
                        "value": EventSuccessMessages.CHATROOM_WORD_GUESSED.value,
                    },
                    message["sid"],
                )

                await manager.broadcast(
                    {
                        "event": SocketOperations.WORD_GUESSED_BROADCAST.value,
                        "value": f"{player_item.get('player_name')} has guessed the word",
                    },
                    message["sid"],
                )

                game_score_details = {
                    "sid": message["sid"],
                    "time_elapsed": message["time_elapsed"],
                    "position": len(game_result["score_details"]) + 1,
                }
                game_result["score_details"].append(game_score_details)

                is_set_game_data = RedisJson().set(
                    redis_key=game_key, redis_value=game_result
                )
                if not is_set_game_data:
                    raise ChatRoomException("The game result are not set in redis.")

                if len(game_result["score_details"]) == len(players) - 1:
                    TimerManager.instance().stop_timer(message["room_id"])
                    logger.info(f"Timer for Game {message['room_id']} stopped")
                    await end_turn(message["room_id"], manager, is_time_up=False)

            else:
                logger.info("The word did'nt match. Hence broadcasting.")
                await manager.broadcast(
                    {
                        "event": SocketOperations.CHAT_ROOM.value,
                        "value": {
                            "word": message["word"],
                            "player_name": player_item.get("player_name"),
                        },
                    },
                    message["sid"],
                )

        except Exception as e:
            logger.error("Error encountered in chat handling.")
            logger.error(e)
            logger.info(traceback.format_exc())
            return
