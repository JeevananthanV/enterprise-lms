import json
from datetime import datetime, date
from decimal import Decimal
from typing import Any, Optional, List, Dict
from uuid import UUID

from app.core.config import settings
from app.core.logging import logger
from app.db.redis import get_redis


class CustomJSONEncoder(json.JSONEncoder):
    """JSON Encoder that handles dates, UUIDs, decimals, and objects with model_dump."""
    def default(self, obj: Any) -> Any:
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, Decimal):
            return float(obj)
        if hasattr(obj, "model_dump"):
            return obj.model_dump(mode="json")
        if hasattr(obj, "dict"):
            return obj.dict()
        return super().default(obj)


class CacheService:
    """Enterprise Redis Caching Service with non-authoritative graceful fallback."""

    def _serialize(self, value: Any) -> str:
        return json.dumps(value, cls=CustomJSONEncoder)

    def _deserialize(self, value: str) -> Any:
        return json.loads(value)

    async def get_cached(self, key: str) -> Optional[Any]:
        """
        Retrieve and deserialize cached payload by key.
        Returns None on cache miss, when caching is disabled, or when Redis is offline.
        """
        if not settings.CACHE_ENABLED:
            return None
        try:
            client = get_redis()
            if client is None:
                return None
            cached_val = await client.get(key)
            if cached_val is None:
                return None
            return self._deserialize(cached_val)
        except Exception as e:
            logger.warning(f"Redis get_cached failed for key '{key}' (falling back to database): {e}")
            return None

    async def set_cached(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
    ) -> bool:
        """
        Serialize and store payload with TTL in Redis.
        Fails silently and returns False if Redis is offline.
        """
        if not settings.CACHE_ENABLED:
            return False
        try:
            client = get_redis()
            if client is None:
                return False
            ttl = ttl_seconds if ttl_seconds is not None else settings.CACHE_DEFAULT_TTL_SECONDS
            serialized = self._serialize(value)
            await client.set(key, serialized, ex=ttl)
            return True
        except Exception as e:
            logger.warning(f"Redis set_cached failed for key '{key}': {e}")
            return False

    async def delete_cached(self, key: str) -> bool:
        """Delete a single cached key."""
        if not settings.CACHE_ENABLED:
            return False
        try:
            client = get_redis()
            if client is None:
                return False
            await client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Redis delete_cached failed for key '{key}': {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a wildcard pattern (e.g. 'courses:catalog:*').
        Returns the number of deleted keys.
        """
        if not settings.CACHE_ENABLED:
            return 0
        try:
            client = get_redis()
            if client is None:
                return 0
            keys: List[str] = await client.keys(pattern)
            if keys:
                return await client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Redis delete_pattern failed for pattern '{pattern}': {e}")
            return 0

    def generate_catalog_key(
        self,
        search: Optional[str] = None,
        category: Optional[str] = None,
        level: Optional[str] = None,
        page: int = 1,
        page_size: int = 12,
    ) -> str:
        """Generate deterministic cache key for public course catalog filters."""
        s = (search or "").strip().lower()
        c = (category or "").strip().lower()
        l = (level or "").strip().lower()
        return f"courses:catalog:s={s}&c={c}&l={l}&p={page}&ps={page_size}"

    def generate_course_details_key(self, course_id: str) -> str:
        return f"course:details:{course_id}"

    def generate_course_curriculum_key(self, course_id: str) -> str:
        return f"course:curriculum:{course_id}"

    def generate_analytics_key(self, scope: str = "platform") -> str:
        return f"analytics:summary:{scope}"

    async def invalidate_course_cache(self, course_id: str) -> None:
        """
        Invalidate all cached entities affected by a course, module, or lesson change:
        1. Course details cache
        2. Course curriculum syllabus cache
        3. All catalog filter permutations
        4. Platform analytics summary cache
        """
        await self.delete_cached(self.generate_course_details_key(course_id))
        await self.delete_cached(self.generate_course_curriculum_key(course_id))
        await self.delete_pattern("courses:catalog:*")
        await self.delete_pattern("analytics:summary:*")
        logger.info(f"Invalidated Redis caches for course '{course_id}'")


cache_service = CacheService()
