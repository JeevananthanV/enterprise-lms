from typing import Optional
import redis.asyncio as aioredis
from app.core.config import settings
from app.core.logging import logger


class RedisManager:
    client: Optional[aioredis.Redis] = None


redis_manager = RedisManager()


async def connect_redis() -> None:
    """Initialize Redis connection pool."""
    try:
        redis_manager.client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_timeout=2.0,
            socket_connect_timeout=2.0,
        )
        logger.info("Redis connection pool initialized")
    except Exception as e:
        logger.warning(f"Redis initialization deferred or failed: {e}")


async def close_redis() -> None:
    """Close Redis connection."""
    if redis_manager.client is not None:
        await redis_manager.client.aclose()
        logger.info("Redis connection closed")


def get_redis() -> Optional[aioredis.Redis]:
    """Dependency / helper to get Redis client."""
    return redis_manager.client


async def check_redis_health() -> bool:
    """Verify Redis connectivity for health checks."""
    try:
        if redis_manager.client is None:
            return False
        await redis_manager.client.ping()
        return True
    except Exception as e:
        logger.warning(f"Redis health check failed or not reachable: {e}")
        return False
