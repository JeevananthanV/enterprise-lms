import pytest
import pytest_asyncio
import uuid
import fnmatch
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, Optional, List
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.redis import redis_manager
from app.services.cache_service import cache_service, CustomJSONEncoder
from app.models.user import User, UserRole
from app.models.course import Course, CourseStatus, CourseLevel
from app.models.module import CourseModule
from app.models.lesson import Lesson, LessonContentType
from app.core.security import create_access_token


class MockAsyncRedis:
    """In-memory async Redis mock with pattern matching, TTL tracking, and error simulation."""

    def __init__(self):
        self.store: Dict[str, str] = {}
        self.ttl_store: Dict[str, int] = {}
        self.simulate_error: bool = False

    async def get(self, key: str) -> Optional[str]:
        if self.simulate_error:
            raise ConnectionError("Simulated Redis connection drop")
        return self.store.get(key)

    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        if self.simulate_error:
            raise ConnectionError("Simulated Redis connection drop")
        self.store[key] = value
        if ex is not None:
            self.ttl_store[key] = ex
        return True

    async def delete(self, *keys: str) -> int:
        if self.simulate_error:
            raise ConnectionError("Simulated Redis connection drop")
        deleted = 0
        for k in keys:
            if k in self.store:
                del self.store[k]
                self.ttl_store.pop(k, None)
                deleted += 1
        return deleted

    async def keys(self, pattern: str) -> List[str]:
        if self.simulate_error:
            raise ConnectionError("Simulated Redis connection drop")
        return [k for k in self.store.keys() if fnmatch.fnmatch(k, pattern)]

    async def ping(self) -> bool:
        if self.simulate_error:
            raise ConnectionError("Simulated Redis connection drop")
        return True

    async def aclose(self) -> None:
        self.store.clear()
        self.ttl_store.clear()


@pytest_asyncio.fixture(autouse=True)
async def setup_redis_mock():
    """Ensure an isolated in-memory Redis mock for every test."""
    mock_redis = MockAsyncRedis()
    original_client = redis_manager.client
    original_enabled = settings.CACHE_ENABLED

    redis_manager.client = mock_redis
    settings.CACHE_ENABLED = True

    yield mock_redis

    redis_manager.client = original_client
    settings.CACHE_ENABLED = original_enabled


@pytest_asyncio.fixture
async def caching_test_data(db_session: AsyncSession):
    """Seed instructor, admin, and published courses for cache testing."""
    uid = uuid.uuid4().hex[:6]

    instructor = User(
        email=f"cache.instructor.{uid}@example.com",
        hashed_password="hashed_password",
        full_name="Cache Instructor",
        role=UserRole.INSTRUCTOR,
        is_active=True,
    )
    admin = User(
        email=f"cache.admin.{uid}@example.com",
        hashed_password="hashed_password",
        full_name="Cache Admin",
        role=UserRole.PLATFORM_ADMIN,
        is_active=True,
    )

    db_session.add_all([instructor, admin])
    await db_session.commit()
    await db_session.refresh(instructor)
    await db_session.refresh(admin)

    course = Course(
        title=f"Redis Performance Masterclass {uid}",
        slug=f"redis-perf-{uid}",
        description="High-throughput caching architectures with Redis and FastAPI",
        instructor_id=instructor.id,
        level=CourseLevel.INTERMEDIATE,
        status=CourseStatus.PUBLISHED,
        category="Backend Engineering",
    )
    db_session.add(course)
    await db_session.commit()
    await db_session.refresh(course)

    module = CourseModule(
        course_id=course.id,
        title="Module 1: Redis Caching Fundamentals",
        order_index=1,
    )
    db_session.add(module)
    await db_session.commit()
    await db_session.refresh(module)

    lesson = Lesson(
        module_id=module.id,
        title="Lesson 1: Key Design and Invalidation",
        slug=f"key-design-{uid}",
        content_type=LessonContentType.TEXT,
        order_index=1,
        is_free_preview=True,
    )
    db_session.add(lesson)
    await db_session.commit()
    await db_session.refresh(lesson)

    return {
        "instructor": instructor,
        "admin": admin,
        "course": course,
        "module": module,
        "lesson": lesson,
    }


def auth_header(user: User) -> Dict[str, str]:
    token = create_access_token(
        subject=user.id,
        role=user.role.value,
        extra_claims={"email": user.email},
    )
    return {"Authorization": f"Bearer {token}"}


# =====================================================================
# Unit Tests for CacheService & CustomJSONEncoder
# =====================================================================

@pytest.mark.asyncio
async def test_cache_service_set_and_get():
    """Verify basic set, get, and TTL functionality."""
    key = "test:entity:123"
    payload = {
        "id": "123",
        "title": "Cached Course",
        "price": 49.99,
        "tags": ["redis", "fastapi"],
    }

    success = await cache_service.set_cached(key, payload, ttl_seconds=180)
    assert success is True

    cached = await cache_service.get_cached(key)
    assert cached is not None
    assert cached["id"] == "123"
    assert cached["title"] == "Cached Course"
    assert cached["tags"] == ["redis", "fastapi"]


@pytest.mark.asyncio
async def test_cache_service_get_miss():
    """Verify cache miss returns None."""
    result = await cache_service.get_cached("nonexistent:key")
    assert result is None


@pytest.mark.asyncio
async def test_cache_service_delete_cached():
    """Verify single key deletion."""
    key = "test:delete:me"
    await cache_service.set_cached(key, {"data": "temp"})
    assert await cache_service.get_cached(key) is not None

    deleted = await cache_service.delete_cached(key)
    assert deleted is True
    assert await cache_service.get_cached(key) is None


@pytest.mark.asyncio
async def test_cache_service_delete_pattern(setup_redis_mock: MockAsyncRedis):
    """Verify pattern-based batch key deletion."""
    await cache_service.set_cached("courses:catalog:s=&c=tech&p=1", {"items": [1]})
    await cache_service.set_cached("courses:catalog:s=&c=design&p=1", {"items": [2]})
    await cache_service.set_cached("course:details:uuid-1", {"name": "Course 1"})

    assert len(setup_redis_mock.store) == 3

    deleted_count = await cache_service.delete_pattern("courses:catalog:*")
    assert deleted_count == 2
    assert "course:details:uuid-1" in setup_redis_mock.store
    assert len(setup_redis_mock.store) == 1


@pytest.mark.asyncio
async def test_cache_service_disabled_mode():
    """Verify CacheService behaves as transparent no-op when CACHE_ENABLED is False."""
    settings.CACHE_ENABLED = False

    key = "disabled:key"
    set_result = await cache_service.set_cached(key, {"data": "test"})
    assert set_result is False

    get_result = await cache_service.get_cached(key)
    assert get_result is None

    del_result = await cache_service.delete_cached(key)
    assert del_result is False

    pat_result = await cache_service.delete_pattern("disabled:*")
    assert pat_result == 0


@pytest.mark.asyncio
async def test_cache_service_offline_fallback():
    """Verify graceful fallback when Redis client is None (offline)."""
    redis_manager.client = None

    key = "offline:key"
    assert await cache_service.set_cached(key, {"val": 1}) is False
    assert await cache_service.get_cached(key) is None
    assert await cache_service.delete_cached(key) is False
    assert await cache_service.delete_pattern("offline:*") == 0


@pytest.mark.asyncio
async def test_cache_service_exception_fallback(setup_redis_mock: MockAsyncRedis):
    """Verify graceful error recovery when Redis commands raise exceptions."""
    setup_redis_mock.simulate_error = True

    key = "error:key"
    assert await cache_service.set_cached(key, {"val": 1}) is False
    assert await cache_service.get_cached(key) is None
    assert await cache_service.delete_cached(key) is False
    assert await cache_service.delete_pattern("error:*") == 0


def test_custom_json_encoder():
    """Verify CustomJSONEncoder handles UUID, datetime, Decimal, and dicts."""
    uid = uuid.uuid4()
    now = datetime.now(timezone.utc)
    dec = Decimal("99.95")

    data = {
        "id": uid,
        "created_at": now,
        "price": dec,
        "name": "Encoder Test",
    }

    import json
    serialized = json.dumps(data, cls=CustomJSONEncoder)
    deserialized = json.loads(serialized)

    assert deserialized["id"] == str(uid)
    assert deserialized["created_at"] == now.isoformat()
    assert deserialized["price"] == 99.95
    assert deserialized["name"] == "Encoder Test"


# =====================================================================
# API End-to-End Caching & Invalidation Tests
# =====================================================================

@pytest.mark.asyncio
async def test_public_course_catalog_caching(
    async_client: AsyncClient, caching_test_data, setup_redis_mock: MockAsyncRedis
):
    """Verify public course catalog response is cached in Redis on read."""
    setup_redis_mock.store.clear()

    # 1. First request fetches from DB and writes to Redis
    res1 = await async_client.get("/api/v1/courses?page=1&page_size=12")
    assert res1.status_code == 200
    data1 = res1.json()
    assert len(data1["items"]) >= 1

    # Check that Redis key was created
    catalog_key = cache_service.generate_catalog_key(page=1, page_size=12)
    assert catalog_key in setup_redis_mock.store

    # 2. Second request hits Redis cache
    res2 = await async_client.get("/api/v1/courses?page=1&page_size=12")
    assert res2.status_code == 200
    data2 = res2.json()
    assert data1 == data2


@pytest.mark.asyncio
async def test_course_details_and_curriculum_caching(
    async_client: AsyncClient, caching_test_data, setup_redis_mock: MockAsyncRedis
):
    """Verify course details and syllabus are cached with appropriate keys."""
    course = caching_test_data["course"]
    setup_redis_mock.store.clear()

    # 1. Fetch details
    details_res = await async_client.get(f"/api/v1/courses/{course.id}")
    assert details_res.status_code == 200
    details_key = cache_service.generate_course_details_key(course.id)
    assert details_key in setup_redis_mock.store

    # 2. Fetch curriculum
    curr_res = await async_client.get(f"/api/v1/courses/{course.id}/curriculum")
    assert curr_res.status_code == 200
    curr_key = cache_service.generate_course_curriculum_key(course.id)
    assert curr_key in setup_redis_mock.store


@pytest.mark.asyncio
async def test_course_update_invalidates_cache(
    async_client: AsyncClient, caching_test_data, setup_redis_mock: MockAsyncRedis
):
    """Verify course updates invalidate course details, curriculum, and catalog caches."""
    instructor = caching_test_data["instructor"]
    course = caching_test_data["course"]

    # Prime caches
    await async_client.get("/api/v1/courses?page=1&page_size=12")
    await async_client.get(f"/api/v1/courses/{course.id}")
    await async_client.get(f"/api/v1/courses/{course.id}/curriculum")

    assert len(setup_redis_mock.store) >= 3

    # Update course
    update_res = await async_client.put(
        f"/api/v1/instructor/courses/{course.id}",
        json={"title": "Updated Redis Architecture Masterclass"},
        headers=auth_header(instructor),
    )
    assert update_res.status_code == 200

    # Verify course caches were purged
    details_key = cache_service.generate_course_details_key(course.id)
    curr_key = cache_service.generate_course_curriculum_key(course.id)
    assert details_key not in setup_redis_mock.store
    assert curr_key not in setup_redis_mock.store

    # Verify subsequent catalog request fetches fresh updated title
    fresh_catalog = await async_client.get("/api/v1/courses?page=1&page_size=12")
    assert fresh_catalog.status_code == 200
    titles = [c["title"] for c in fresh_catalog.json()["items"]]
    assert "Updated Redis Architecture Masterclass" in titles


@pytest.mark.asyncio
async def test_curriculum_mutation_invalidates_course_cache(
    async_client: AsyncClient, caching_test_data, setup_redis_mock: MockAsyncRedis
):
    """Verify adding a module or lesson automatically invalidates cached course syllabus."""
    instructor = caching_test_data["instructor"]
    course = caching_test_data["course"]

    # Prime curriculum cache
    await async_client.get(f"/api/v1/courses/{course.id}/curriculum")
    curr_key = cache_service.generate_course_curriculum_key(course.id)
    assert curr_key in setup_redis_mock.store

    # Create new module
    mod_res = await async_client.post(
        f"/api/v1/instructor/courses/{course.id}/modules",
        json={"title": "Module 2: Advanced Caching Strategies", "order_index": 2},
        headers=auth_header(instructor),
    )
    assert mod_res.status_code == 201

    # Curriculum cache must be invalidated
    assert curr_key not in setup_redis_mock.store


@pytest.mark.asyncio
async def test_analytics_summary_caching_and_rbac(
    async_client: AsyncClient, caching_test_data, setup_redis_mock: MockAsyncRedis
):
    """Verify platform analytics endpoint is cached and restricted to admins."""
    admin = caching_test_data["admin"]
    instructor = caching_test_data["instructor"]
    setup_redis_mock.store.clear()

    # Instructor cannot access platform analytics -> 403
    forbidden_res = await async_client.get(
        "/api/v1/analytics/summary",
        headers=auth_header(instructor),
    )
    assert forbidden_res.status_code == 403

    # Admin access succeeds -> 200 (computed fresh from DB)
    admin_res = await async_client.get(
        "/api/v1/analytics/summary",
        headers=auth_header(admin),
    )
    assert admin_res.status_code == 200
    analytics_data = admin_res.json()
    assert "total_users" in analytics_data
    assert "total_courses" in analytics_data
    assert "total_enrollments" in analytics_data
    assert analytics_data["from_cache"] is False

    # Verify cached in Redis
    analytics_key = cache_service.generate_analytics_key("platform")
    assert analytics_key in setup_redis_mock.store

    # Repeated call returns cached metrics with from_cache=True
    cached_res = await async_client.get(
        "/api/v1/analytics/summary",
        headers=auth_header(admin),
    )
    assert cached_res.status_code == 200
    cached_data = cached_res.json()
    assert cached_data["from_cache"] is True
    assert cached_data["total_users"] == analytics_data["total_users"]
    assert cached_data["total_courses"] == analytics_data["total_courses"]


@pytest.mark.asyncio
async def test_api_graceful_fallback_when_redis_offline(
    async_client: AsyncClient, caching_test_data, setup_redis_mock: MockAsyncRedis
):
    """Verify all cached APIs continue functioning seamlessly without 500 errors when Redis is down."""
    course = caching_test_data["course"]
    admin = caching_test_data["admin"]

    # Simulate Redis connection failure
    setup_redis_mock.simulate_error = True

    # Catalog still works via DB
    catalog_res = await async_client.get("/api/v1/courses")
    assert catalog_res.status_code == 200

    # Course details still works via DB
    details_res = await async_client.get(f"/api/v1/courses/{course.id}")
    assert details_res.status_code == 200

    # Analytics still works via DB
    analytics_res = await async_client.get(
        "/api/v1/analytics/summary",
        headers=auth_header(admin),
    )
    assert analytics_res.status_code == 200
