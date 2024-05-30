from enum import Enum

class RedisOperations(Enum):
    JSON_SET = "JSON.SET"
    JSON_GET = "JSON.GET"
    JSON_ARRAY_LENGTH = "JSON.ARRLEN"
    JSON_ARRAY_APPEND = "JSON.ARRAPPEND"
    JSON_NUMBER_INCR_BY = "JSON.NUMINCRBY"
    
