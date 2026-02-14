import redis
import logging
from app.config import settings

logger = logging.getLogger("gpa.redis")

try:
    # Initialize synchronous Redis client
    # decode_responses=True returns strings instead of bytes
    redis_client = redis.Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5
    )
    # Test connection
    redis_client.ping()
    logger.info(f"Connected to Redis at {settings.REDIS_URL}")
except Exception as e:
    logger.warning(f"Failed to connect to Redis: {e}. Falling back to in-memory (NOT RECOMMENDED FOR PRODUCTION).")
    redis_client = None
