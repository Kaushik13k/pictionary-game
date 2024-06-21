from init.redis_init import redis_init


def get_room_ids():
    redis_keys = redis_init.keys("*")
    rooms = []
    for key in redis_keys:
        room_id = (key.decode()).split("room_id_players:")[1]
        rooms.append(room_id)

    return rooms
