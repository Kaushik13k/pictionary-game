import json
import logging
import traceback

from init.redis_init import redis_init
from enums.redis_locations import RedisLocations
from enums.redis_operations import RedisOperations


logger = logging.getLogger(__name__)


class RedisJson:
    def get(self, key):
        pass

    def set(
        self, redis_key: str, redis_value: str, location: str = RedisLocations.NIL.value
    ) -> bool:
        try:
            logger.info(f"Redis set function called for key {redis_key}")
            result = redis_init.execute_command(
                RedisOperations.JSON_SET.value,
                redis_key,
                f"${location}",
                json.dumps(redis_value),
            )
            if result.decode("utf-8") == "OK":
                logger.info(f"Redis set operation successful.")
                return True
            logger.error(f"Error in Redis set operation.")
            return False
        except Exception as e:
            logger.error(f"Error in Redis set operation for key {redis_key}")
            logger.error(e)
            logger.error(traceback.format_exc())
            return False

    # def delete(self, key):
    #     pass

    # def append(self, key):
    #     pass
