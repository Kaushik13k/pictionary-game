import logging
import traceback
from fastapi import APIRouter
from init.redis_init import redis_init

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/rooms", tags=["Rooms"], responses={404: {"description": "Not found"}})
async def fetch_rooms():
    try:
        logger.info("Fetching rooms..")
        redis_keys = redis_init.keys('*')
        rooms = []
        for key in redis_keys:
            room_id = (key.decode()).split("room_id:")[1]
            rooms.append(room_id)
        return {"rooms": rooms, "response": 200}
    except Exception as e:
        logger.error(f"There was error fetching rooms: {e}")
        logger.info(traceback.format_exc())
        return {"response": 404}