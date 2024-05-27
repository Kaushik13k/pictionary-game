from fastapi import APIRouter
from init.redis_init import redis_init

router = APIRouter()

@router.get("/rooms", tags=["Rooms"], responses={404: {"description": "Not found"}})
async def fetch_rooms():
    print("inside fetch rooms")
    keys = redis_init.keys('*')
    rooms = []
    print(keys)
    for key in keys:
        room_id = (key.decode()).split("room_id:")[1]
        print(room_id)
        rooms.append(room_id)
    return {"rooms": rooms, "response": 200}