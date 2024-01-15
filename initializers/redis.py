import redis
import os

REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

r = redis.Redis(
  host='localhost', 
  port=6379,
  password=REDIS_PASSWORD,
)

