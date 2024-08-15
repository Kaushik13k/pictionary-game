from enum import Enum


class RedisIdentityKeys(Enum):
    PLAYERS = "room_id_players"
    GAMES = "room_id_games"
