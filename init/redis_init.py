import redis
# REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
# REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
# REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

redis_init = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)