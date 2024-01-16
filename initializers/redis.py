import redis
import os

REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

if os.getenv('LOCAL_ENV') == 'true':
  HOST = "localhost" 
else:
  HOST = "redis"
r = redis.Redis(
  host=HOST, 
  port=6379,
  password=REDIS_PASSWORD,
)

