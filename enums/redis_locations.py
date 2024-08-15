from enum import Enum


class RedisLocations(Enum):
    NIL = ""
    ROOT = "$"
    MEMBERS = ".members"
