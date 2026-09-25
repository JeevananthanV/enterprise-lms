import pytest
import pytest_asyncio
import uuid
from httpx import AsyncClient

from app.core.security import hash_password
from app.models.user import User, UserRole


@pytest_asyncio.fixture
async def setup_e2e_seed_data(db_session):
    admin = User(
        email=f"e2e_admin_{uuid.uuid4().hex[:6]}@example.com",
        full_name="E2E Platform Admin",
        hashed_password=hash_password("AdminPass123!"),
        role=UserRole.PLATFORM_ADMIN,
        is_active=True,
    )
    inst = User(
        email=f"e2e_instructor_{uuid.uuid4().hex[:6]}@example.com",
        full_name="E2E Instructor",
        hashed_password=hash_password("InstPass123!"),
        role=UserRole.INSTRUCTOR,
        is_active=True,
    )
    student = User(
        email=f"e2e_student_{uuid.uuid4().hex[:6]}@example.com",
        full_name="E2E Student",
        hashed_password=hash_password("StudentPass123!"),
        role=UserRole.STUDENT,
        is_active=True,
    )
    db_session.add_all([admin, inst, student])
    await db_session.commit()
    for u in [admin, inst, student]:
        await db_session.refresh(u)

    return {
        "admin": admin, "admin_pwd": "AdminPass123!",
        "inst": inst, "inst_pwd": "InstPass123!",
        "student": student, "student_pwd": "StudentPass123!",
    }


@pytest.mark.asyncio
async def test_e2e_instructor_authoring_journey(async_client: AsyncClient, setup_e2e_seed_data):
    """
    E2E Instructor Flow:
    Login -> Create Course (Draft) -> Add Modules -> Add Lessons -> Add MongoDB Content -> Publish -> Analytics
    """
    data = setup_e2e_seed_data

    # 1. Login
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": data["inst"].email, "password": data["inst_pwd"]},
    )
    assert login_res.status_code == 200
    inst_token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {inst_token}"}

    # 2. Create Course in DRAFT mode
    course_res = await async_client.post(
        "/api/v1/instructor/courses",
        headers=headers,
        json={
            "title": "Full Stack Cloud Architecture",
            "short_description": "Comprehensive cloud design from scratch",
            "description": "A complete masterclass in full stack cloud architecture covering microservices, caching, and resiliency.",
            "category": "Cloud Computing",
            "level": "INTERMEDIATE",
            "price": 0.0,
        },
    )
    assert course_res.status_code == 201
    course_data = course_res.json()
    course_id = course_data["id"]
    assert course_data["status"] == "DRAFT"

    # 3. Add Module
    module_res = await async_client.post(
        f"/api/v1/instructor/courses/{course_id}/modules",
        headers=headers,
        json={"title": "Module 1: Foundations", "order_index": 1},
    )
    assert module_res.status_code == 201
    module_id = module_res.json()["id"]

    # 4. Add Lesson
    lesson_res = await async_client.post(
        f"/api/v1/instructor/modules/{module_id}/lessons",
        headers=headers,
        json={
            "title": "Lesson 1: Microservices Design",
            "content_type": "TEXT",
            "order_index": 1,
            "duration_minutes": 25,
            "is_free_preview": True,
        },
    )
    assert lesson_res.status_code == 201
    lesson_id = lesson_res.json()["id"]

    # 5. Add MongoDB Flexible Content
    content_res = await async_client.post(
        f"/api/v1/lessons/{lesson_id}/content",
        headers=headers,
        json={
            "content_type": "RICH_TEXT",
            "body": "<h1>Microservices Architecture</h1><p>Event-driven microservices pattern.</p>",
            "video_metadata": {
                "video_url": "https://cdn.example.com/hls/lesson1.m3u8",
                "duration_seconds": 1500,
                "resolution": "1080p",
            },
            "pdf_metadata": {
                "file_url": "https://cdn.example.com/docs/slides.pdf",
                "file_name": "slides.pdf",
                "page_count": 32,
            },
        },
    )
    assert content_res.status_code == 201
    assert content_res.json()["version"] == 1

    # 6. Publish Lesson Content
    pub_content_res = await async_client.post(
        f"/api/v1/lessons/{lesson_id}/content/publish",
        headers=headers,
    )
    assert pub_content_res.status_code == 200
    assert pub_content_res.json()["is_published"] is True

    # 7. Check Publish Checklist and Publish Course
    checklist_res = await async_client.get(
        f"/api/v1/instructor/courses/{course_id}/publish-checklist",
        headers=headers,
    )
    assert checklist_res.status_code == 200
    assert checklist_res.json()["is_publishable"] is True

    pub_course_res = await async_client.post(
        f"/api/v1/instructor/courses/{course_id}/publish",
        headers=headers,
    )
    assert pub_course_res.status_code == 200
    assert pub_course_res.json()["status"] == "PUBLISHED"


@pytest.mark.asyncio
async def test_e2e_student_learning_and_certification_journey(async_client: AsyncClient, setup_e2e_seed_data):
    """
    E2E Student Flow:
    Login -> Browse Catalog -> View Details -> Enroll -> Course Player -> Lesson Progress
    """
    data = setup_e2e_seed_data

    # Setup a published course using instructor credentials first
    inst_login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": data["inst"].email, "password": data["inst_pwd"]},
    )
    inst_token = inst_login.json()["access_token"]
    inst_headers = {"Authorization": f"Bearer {inst_token}"}

    c_res = await async_client.post(
        "/api/v1/instructor/courses",
        headers=inst_headers,
        json={
            "title": "Data Engineering at Scale",
            "short_description": "Data lakes and warehouses at scale",
            "description": "Comprehensive course on data engineering at scale with practical labs and pipelines.",
            "level": "ADVANCED",
            "price": 0.0,
        },
    )
    assert c_res.status_code == 201
    course_id = c_res.json()["id"]

    m_res = await async_client.post(
        f"/api/v1/instructor/courses/{course_id}/modules",
        headers=inst_headers,
        json={"title": "Data Lakes", "order_index": 1},
    )
    assert m_res.status_code == 201
    module_id = m_res.json()["id"]

    l_res = await async_client.post(
        f"/api/v1/instructor/modules/{module_id}/lessons",
        headers=inst_headers,
        json={"title": "Apache Iceberg & BigLake", "content_type": "TEXT", "order_index": 1},
    )
    assert l_res.status_code == 201
    lesson_id = l_res.json()["id"]

    # Publish
    pub_res = await async_client.post(f"/api/v1/instructor/courses/{course_id}/publish", headers=inst_headers)
    assert pub_res.status_code == 200

    # 1. Student Login
    stud_login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": data["student"].email, "password": data["student_pwd"]},
    )
    assert stud_login.status_code == 200
    student_token = stud_login.json()["access_token"]
    stud_headers = {"Authorization": f"Bearer {student_token}"}

    # 2. Browse Catalog
    catalog_res = await async_client.get("/api/v1/courses", headers=stud_headers)
    assert catalog_res.status_code == 200
    assert any(c["id"] == course_id for c in catalog_res.json()["items"])

    # 3. View Course Details & Syllabus
    detail_res = await async_client.get(f"/api/v1/courses/{course_id}", headers=stud_headers)
    assert detail_res.status_code == 200
    assert detail_res.json()["title"] == "Data Engineering at Scale"

    # 4. Enroll in Course
    enroll_res = await async_client.post(
        f"/api/v1/courses/{course_id}/enroll",
        headers=stud_headers,
    )
    assert enroll_res.status_code in [200, 201]

    # 5. Check My Learning
    my_learn_res = await async_client.get("/api/v1/me/enrollments", headers=stud_headers)
    assert my_learn_res.status_code == 200
    assert any(item["course"]["id"] == course_id for item in my_learn_res.json())

    # 6. Load Course Player
    player_res = await async_client.get(f"/api/v1/courses/{course_id}/player", headers=stud_headers)
    assert player_res.status_code == 200
    assert player_res.json()["total_lessons"] == 1
    assert len(player_res.json()["modules"][0]["lessons"]) == 1

    # 7. Complete Lesson Progress
    prog_res = await async_client.post(
        f"/api/v1/lessons/{lesson_id}/progress",
        headers=stud_headers,
        json={"is_completed": True, "progress_percent": 100.0, "time_spent_seconds": 300},
    )
    assert prog_res.status_code == 200
    assert prog_res.json()["is_completed"] is True

    # 8. Check Progress Dashboard & Course Player
    updated_player = await async_client.get(f"/api/v1/courses/{course_id}/player", headers=stud_headers)
    assert updated_player.status_code == 200
    assert updated_player.json()["progress_percentage"] == 100.0
    assert updated_player.json()["completed_lessons"] == 1

    my_prog = await async_client.get("/api/v1/me/progress", headers=stud_headers)
    assert my_prog.status_code == 200
    assert my_prog.json()["total_enrolled_courses"] == 1
    assert my_prog.json()["completed_courses"] == 1
    assert my_prog.json()["overall_completion_percentage"] == 100.0


@pytest.mark.asyncio
async def test_e2e_admin_governance_journey(async_client: AsyncClient, setup_e2e_seed_data):
    """
    E2E Admin Flow:
    Login -> Metrics Summary -> Probe Security -> Health Check
    """
    data = setup_e2e_seed_data

    # 1. Admin Login
    admin_login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": data["admin"].email, "password": data["admin_pwd"]},
    )
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Query Analytics Summary
    analytics_res = await async_client.get("/api/v1/analytics/summary", headers=admin_headers)
    assert analytics_res.status_code == 200
    summary = analytics_res.json()
    assert "total_users" in summary
    assert "total_courses" in summary

    # 3. Probe Admin Access Endpoint
    probe_res = await async_client.get("/api/v1/users/admin-only", headers=admin_headers)
    assert probe_res.status_code == 200
    assert probe_res.json()["role"] == "PLATFORM_ADMIN"

    # 4. System Health Check
    health_res = await async_client.get("/health")
    assert health_res.status_code == 200
    assert health_res.json()["status"] == "healthy"
