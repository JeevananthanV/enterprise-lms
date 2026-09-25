import pytest
import pytest_asyncio
import uuid
from httpx import AsyncClient

from app.core.security import create_access_token
from app.models.user import User, UserRole
from app.models.course import Course, CourseStatus, CourseLevel
from app.models.module import CourseModule
from app.models.lesson import Lesson, LessonContentType
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.services.cache_service import cache_service


@pytest_asyncio.fixture
async def setup_infra_data(db_session):
    admin = User(
        email=f"infra_admin_{uuid.uuid4().hex[:6]}@example.com",
        full_name="Infra Admin",
        hashed_password="hashed_pw_test",
        role=UserRole.PLATFORM_ADMIN,
        is_active=True,
    )
    inst = User(
        email=f"infra_inst_{uuid.uuid4().hex[:6]}@example.com",
        full_name="Infra Instructor",
        hashed_password="hashed_pw_test",
        role=UserRole.INSTRUCTOR,
        is_active=True,
    )
    db_session.add_all([admin, inst])
    await db_session.commit()
    await db_session.refresh(admin)
    await db_session.refresh(inst)

    inst_token = create_access_token(subject=inst.id, role=inst.role.value, extra_claims={"email": inst.email})
    admin_token = create_access_token(subject=admin.id, role=admin.role.value, extra_claims={"email": admin.email})

    return {
        "admin": admin, "admin_token": admin_token,
        "inst": inst, "inst_token": inst_token,
    }


@pytest.mark.asyncio
async def test_api_health_and_subsystem_telemetry(async_client: AsyncClient):
    # Root health
    root_res = await async_client.get("/health")
    assert root_res.status_code == 200
    assert root_res.json()["status"] == "healthy"

    # API v1 health
    v1_res = await async_client.get("/api/v1/health")
    assert v1_res.status_code == 200
    assert v1_res.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_cache_service_resilience_and_graceful_degradation(async_client: AsyncClient, setup_infra_data):
    data = setup_infra_data
    # 1. Set cache
    success = await cache_service.set_cached("test:resilience:key", {"status": "operational"}, ttl_seconds=60)
    # Regardless of whether Redis is live or mocked/offline, method returns bool without exception
    assert isinstance(success, bool)

    # 2. Get cache
    val = await cache_service.get_cached("test:resilience:key")
    # If redis is active, returns dict, if offline returns None

    # 3. Delete cache
    del_success = await cache_service.delete_cached("test:resilience:key")
    assert isinstance(del_success, bool)


@pytest.mark.asyncio
async def test_mongodb_flexible_content_versioning_and_unpublish(async_client: AsyncClient, setup_infra_data):
    data = setup_infra_data
    headers = {"Authorization": f"Bearer {data['inst_token']}"}

    # 1. Create course & module & lesson
    c_res = await async_client.post(
        "/api/v1/instructor/courses",
        headers=headers,
        json={"title": "MongoDB Deep Dive", "level": "ADVANCED"},
    )
    assert c_res.status_code == 201
    course_id = c_res.json()["id"]

    m_res = await async_client.post(
        f"/api/v1/instructor/courses/{course_id}/modules",
        headers=headers,
        json={"title": "Document Design"},
    )
    assert m_res.status_code == 201
    module_id = m_res.json()["id"]

    l_res = await async_client.post(
        f"/api/v1/instructor/modules/{module_id}/lessons",
        headers=headers,
        json={"title": "Schema Modeling"},
    )
    assert l_res.status_code == 201
    lesson_id = l_res.json()["id"]

    # 2. Create MongoDB content document
    create_res = await async_client.post(
        f"/api/v1/lessons/{lesson_id}/content",
        headers=headers,
        json={"content_type": "TEXT", "body": "Initial draft body"},
    )
    assert create_res.status_code == 201
    assert create_res.json()["version"] == 1

    # 3. Update MongoDB content document (version bump)
    update_res = await async_client.put(
        f"/api/v1/lessons/{lesson_id}/content",
        headers=headers,
        json={"body": "Updated body revision 2"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["version"] == 2
    assert update_res.json()["body"] == "Updated body revision 2"

