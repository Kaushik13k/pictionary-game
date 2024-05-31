import json
import logging
import traceback

from init.redis_init import redis_init
from services.socket_event import SocketEvent

from enums.redis_operations import RedisOperations
from enums.socket_operations import SocketOperations
import asyncio


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GUESS_TIME = 5
    

class StartGame(SocketEvent):
    async def handle(self, sio: str, socket_id: str, message: str):
        try:
            room_id = json.loads(message)['room_id']
            logger.info(f"the recieved items are: {sio}, {socket_id}, {message}")
            redis_key = f"room_id_players:{room_id}"
            game_key = f"room_id_game:{room_id}"
            game = await self.get_game_data(sio, socket_id, game_key)
            user = self.get_user_data(redis_key)
            players = user["members"]
            drawer_id = players[0]['player_id']
            logger.info(f"Starting game for room {room_id} with drawer {drawer_id}")

            await sio.emit(SocketOperations.START_TURN.value, {'drawer_id': drawer_id}, room=socket_id)
            logger.info(f"Emitted start_turn event for room {socket_id}")

            await asyncio.sleep(GUESS_TIME)
            await sio.emit(SocketOperations.END_TURN.value, room=socket_id)
            logger.info(f"Emitted end_turn event for room {socket_id}")

            game['turns'] = game.get('turns', 0) + 1
            self.set_game_data(game_key, game)

            if game['turns'] >= len(players):
                await self.end_round(sio, socket_id, game, game_key)

            user["members"] = players[1:] + players[:1]
            logger.info(f"New player order: {players}")
            self.set_user_data(redis_key, user)

            await self.handle(sio, socket_id, message=message)

        except Exception as e:
            logger.error(e)

    async def get_game_data(self, sio, socket_id, game_key):
        game = redis_init.execute_command(RedisOperations.JSON_GET.value, game_key)
        logger.info(f"Game data: {game}")
        if game is None:
            game = {}
            if game.get('rounds') is None:
                game['rounds'] = 1
            await sio.emit(SocketOperations.START_ROUND.value, {"message": f"Round {game['rounds']} Starts."}, room=socket_id)
            self.set_game_data(game_key, game)
        else:
            game = json.loads(game)
            if game["turns"] == 0:
                await sio.emit(SocketOperations.START_ROUND.value, {"message": f"Round {game['rounds']} Starts."}, room=socket_id)
        return game

    def set_game_data(self, game_key, game):
        result_game = redis_init.execute_command(RedisOperations.JSON_SET.value, game_key, "$", json.dumps(game))

    def get_user_data(self, redis_key):
        user = json.loads(redis_init.execute_command(RedisOperations.JSON_GET.value, redis_key))
        logger.info(f"User data: {user}")
        return user

    def set_user_data(self, redis_key, user):
        result_players = redis_init.execute_command(RedisOperations.JSON_SET.value, redis_key, "$", json.dumps(user))
        logger.info(f"Set data in Redis for key {redis_key}")

    async def end_round(self, sio, socket_id, game, game_key):
        await sio.emit(SocketOperations.END_ROUND.value, {"message": f"Round {game['rounds']} ends."}, room=socket_id)
        redis_init.execute_command(RedisOperations.JSON_NUMBER_INCR_BY.value, game_key, '$.rounds', 1)
        result_game = redis_init.execute_command(RedisOperations.JSON_SET.value, game_key, "$.turns", 0)