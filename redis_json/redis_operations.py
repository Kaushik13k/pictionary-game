import json
import logging
import traceback
from typing import Optional

from init.redis_init import redis_init
from enums.redis_locations import RedisLocations
from enums.redis_operations import RedisOperations


logger = logging.getLogger(__name__)


class RedisJson:
    def get(
        self, redis_key: str, location: str = RedisLocations.ROOT.value
    ) -> Optional[dict]:
        try:
            logger.info(
                f"Redis get operation called for key {redis_key}, location {location}"
            )
            result = redis_init.execute_command(
                RedisOperations.JSON_GET.value, redis_key, location
            )
            if result:
                logger.info(f"Redis get operation successful.")
                return result
            logger.info(
                f"The result was None. The key is not created yet/Wrong key provided."
            )
            return None
        except Exception as e:
            logger.error(f"Error in Redis get operation for key {redis_key}")
            logger.error(e)
            logger.error(traceback.format_exc())
            return None

    def set(
        self,
        redis_key: str,
        redis_value: dict,
        location: str = RedisLocations.ROOT.value,
    ) -> bool:
        try:
            logger.info(f"Redis set operation called for key {redis_key}")
            result = redis_init.execute_command(
                RedisOperations.JSON_SET.value,
                redis_key,
                location,
                json.dumps(redis_value),
            )
            if result and result.decode("utf-8") == "OK":
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

    def append(
        self,
        redis_key: str,
        redis_value: str,
        location: str = RedisLocations.ROOT.value,
    ) -> bool:
        try:
            logger.info(f"Redis append operation called for key {redis_key}")
            result = redis_init.execute_command(
                RedisOperations.JSON_ARRAY_APPEND.value,
                redis_key,
                location,
                json.dumps(redis_value),
            )

            if result:
                logger.info(f"Redis append operation successful.")
                return True
            logger.error(f"Error in Redis append operation.")
            return False
        except Exception as e:
            logger.error(f"Error in Redis append operation for key {redis_key}")
            logger.error(e)
            logger.error(traceback.format_exc())
            return False

    def length(
        self, redis_key: str, location: str = RedisLocations.ROOT.value
    ) -> Optional[int]:
        try:
            logger.info(f"Redis length operation called for key {redis_key}")
            result = redis_init.execute_command(
                RedisOperations.JSON_ARRAY_LENGTH.value, redis_key, location
            )
            if result:
                logger.info(f"Redis length operation successful.")
                return int(result)
            logger.error(f"Error in Redis length operation.")
            return None
        except Exception as e:
            logger.error(f"Error in Redis length operation for key {redis_key}")
            logger.error(e)
            logger.error(traceback.format_exc())
            return None
