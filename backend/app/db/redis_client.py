import redis
import logging
from app.config import settings

logger = logging.getLogger("gpa.redis")

try:
    
    
    redis_client = redis.Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5
    )
    
    redis_client.ping()
    logger.info(f"Connected to Redis at {settings.REDIS_URL}")
except Exception as e:
    logger.warning(f"Failed to connect to Redis: {e}. Falling back to in-memory (NOT RECOMMENDED FOR PRODUCTION).")
    redis_client = None
