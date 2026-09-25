import pytest
import pytest_asyncio
import uuid
import jwt
from httpx import AsyncClient
from datetime import datetime, timezone, timedelta

from app.core.config import settings
from app.core.security import create_access_token, hash_password
from app.models.user import User, UserRole
from app.models.course import Course, CourseStatus, CourseLevel
from app.models.module import CourseModule
from app.models.lesson import Lesson, LessonContentType


@pytest_asyncio.fixture
async def setup_security_fixtures(db_session):
    admin = User(
        email=f"sec_admin_{uuid.uuid4().hex[:6]}@example.com",
        full_name="Security Admin",
        hashed_password=hash_password("AdminPass123!"),
        role=UserRole.PLATFORM_ADMIN,
        is_active=True,
    )
    inst_a = User(
        email=f"inst_a_{uuid.uuid4().hex[:6]}@example.com",
        full_name="Instructor Alpha",
        hashed_password=hash_password("InstPass123!"),
        role=UserRole.INSTRUCTOR,
        is_active=True,
    )
    inst_b = User(
        email=f"inst_b_{uuid.uuid4().hex[:6]}@example.com",
        full_name="Instructor Beta",
        hashed_password=hash_password("InstPass123!"),
        role=UserRole.INSTRUCTOR,
        is_active=True,
    )
    student_1 = User(
        email=f"stud_1_{uuid.uuid4().hex[:6]}@example.com",
        full_name="Student One",
        hashed_password=hash_password("StudPass123!"),
        role=UserRole.STUDENT,
        is_active=True,
    )
    student_2 = User(
        email=f"stud_2_{uuid.uuid4().hex[:6]}@example.com",
        full_name="Student Two",
        hashed_password=hash_password("StudPass123!"),
        role=UserRole.STUDENT,
        is_active=True,
    )
    db_session.add_all([admin, inst_a, inst_b, student_1, student_2])
    await db_session.commit()
    for u in [admin, inst_a, inst_b, student_1, student_2]:
        await db_session.refresh(u)

    # Course owned by Instructor A
    course_a = Course(
        instructor_id=inst_a.id,
        title="SecOps Masterclass",
        slug=f"secops-masterclass-{uuid.uuid4().hex[:6]}",
        status=CourseStatus.PUBLISHED,
        level=CourseLevel.ADVANCED,
        price=0.0,
    )
    db_session.add(course_a)
    await db_session.commit()
    await db_session.refresh(course_a)

    module_a = CourseModule(course_id=course_a.id, title="Module 1: Defense", order_index=1, is_published=True)
    db_session.add(module_a)
    await db_session.commit()
    await db_session.refresh(module_a)

    lesson_a = Lesson(
        module_id=module_a.id,
        title="Lesson 1: Zero Trust",
        slug="zero-trust",
        content_type=LessonContentType.TEXT,
        order_index=1,
        is_published=True,
        is_free_preview=False,
    )
    db_session.add(lesson_a)
    await db_session.commit()
    await db_session.refresh(lesson_a)

    admin_token = create_access_token(subject=admin.id, role=admin.role.value, extra_claims={"email": admin.email})
    inst_a_token = create_access_token(subject=inst_a.id, role=inst_a.role.value, extra_claims={"email": inst_a.email})
    inst_b_token = create_access_token(subject=inst_b.id, role=inst_b.role.value, extra_claims={"email": inst_b.email})
    student_1_token = create_access_token(subject=student_1.id, role=student_1.role.value, extra_claims={"email": student_1.email})
    student_2_token = create_access_token(subject=student_2.id, role=student_2.role.value, extra_claims={"email": student_2.email})

    return {
        "admin": admin, "admin_token": admin_token,
        "inst_a": inst_a, "inst_a_token": inst_a_token,
        "inst_b": inst_b, "inst_b_token": inst_b_token,
        "student_1": student_1, "student_1_token": student_1_token,
        "student_2": student_2, "student_2_token": student_2_token,
        "course_a": course_a, "module_a": module_a, "lesson_a": lesson_a,
    }


@pytest.mark.asyncio
async def test_jwt_tampering_and_expiration_security(async_client: AsyncClient, setup_security_fixtures):
    data = setup_security_fixtures
    url = "/api/v1/auth/me"

    # 1. Missing Authorization header
    res = await async_client.get(url)
    assert res.status_code == 401

    # 2. Malformed token
    res = await async_client.get(url, headers={"Authorization": "InvalidScheme token123"})
    assert res.status_code == 401

    res = await async_client.get(url, headers={"Authorization": "Bearer not.a.valid.jwt"})
    assert res.status_code == 401

    # 3. Tampered signature (signed with wrong secret key)
    fake_token = jwt.encode(
        {"sub": str(data["admin"].id), "role": "PLATFORM_ADMIN", "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())},
        "wrong_attacker_secret_key_at_least_32_bytes_long",
        algorithm="HS256",
    )
    res = await async_client.get(url, headers={"Authorization": f"Bearer {fake_token}"})
    assert res.status_code == 401

    # 4. Expired token
    expired_token = jwt.encode(
        {"sub": str(data["admin"].id), "role": "PLATFORM_ADMIN", "exp": int((datetime.now(timezone.utc) - timedelta(minutes=10)).timestamp())},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    res = await async_client.get(url, headers={"Authorization": f"Bearer {expired_token}"})
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_rbac_privilege_escalation_denial(async_client: AsyncClient, setup_security_fixtures):
    data = setup_security_fixtures

    # Student cannot access Admin endpoints
    res = await async_client.get(
        "/api/v1/users/admin-only",
        headers={"Authorization": f"Bearer {data['student_1_token']}"},
    )
    assert res.status_code == 403

    # Student cannot access Instructor course creation
    res = await async_client.post(
        "/api/v1/instructor/courses",
        headers={"Authorization": f"Bearer {data['student_1_token']}"},
        json={"title": "Hacked Course", "level": "BEGINNER"},
    )
    assert res.status_code == 403

    # Instructor cannot access Admin diagnostics / probe
    res = await async_client.get(
        "/api/v1/users/admin-only",
        headers={"Authorization": f"Bearer {data['inst_a_token']}"},
    )
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_cross_instructor_resource_isolation(async_client: AsyncClient, setup_security_fixtures):
    data = setup_security_fixtures
    course_a = data["course_a"]

    # Instructor B attempts to modify Instructor A's course metadata
    res = await async_client.put(
        f"/api/v1/instructor/courses/{course_a.id}",
        headers={"Authorization": f"Bearer {data['inst_b_token']}"},
        json={"title": "Hijacked Course Title"},
    )
    assert res.status_code == 403

    # Instructor B attempts to add a module to Instructor A's course
    res = await async_client.post(
        f"/api/v1/instructor/courses/{course_a.id}/modules",
        headers={"Authorization": f"Bearer {data['inst_b_token']}"},
        json={"title": "Malicious Module"},
    )
    assert res.status_code == 403

    # Instructor B attempts to publish/unpublish Instructor A's course
    res = await async_client.post(
        f"/api/v1/instructor/courses/{course_a.id}/unpublish",
        headers={"Authorization": f"Bearer {data['inst_b_token']}"},
    )
    assert res.status_code == 403

    # Instructor B attempts to add MongoDB content to Instructor A's lesson
    res = await async_client.post(
        f"/api/v1/lessons/{data['lesson_a'].id}/content",
        headers={"Authorization": f"Bearer {data['inst_b_token']}"},
        json={"content_type": "TEXT", "body": "Malicious content injection"},
    )
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_cross_student_progress_and_submission_isolation(async_client: AsyncClient, setup_security_fixtures):
    data = setup_security_fixtures
    course_a = data["course_a"]

    # Enroll Student 1
    res1 = await async_client.post(
        f"/api/v1/courses/{course_a.id}/enroll",
        headers={"Authorization": f"Bearer {data['student_1_token']}"},
    )
    assert res1.status_code == 201

    # Student 2 cannot see Student 1's enrollment in their profile
    res_enr = await async_client.get(
        "/api/v1/me/enrollments",
        headers={"Authorization": f"Bearer {data['student_2_token']}"},
    )
    assert res_enr.status_code == 200
    assert len(res_enr.json()) == 0

    # Student 2 accessing course player shows unenrolled
    res_player = await async_client.get(
        f"/api/v1/courses/{course_a.id}/player",
        headers={"Authorization": f"Bearer {data['student_2_token']}"},
    )
    assert res_player.status_code == 200
    assert res_player.json()["is_enrolled"] is False

    # When Student 2 enrolls, their progress is independent (0%)
    res_enr2 = await async_client.post(
        f"/api/v1/courses/{course_a.id}/enroll",
        headers={"Authorization": f"Bearer {data['student_2_token']}"},
    )
    assert res_enr2.status_code == 201

    res_prog2 = await async_client.get(
        "/api/v1/me/progress",
        headers={"Authorization": f"Bearer {data['student_2_token']}"},
    )
    assert res_prog2.status_code == 200
    assert res_prog2.json()["total_enrolled_courses"] == 1
    assert res_prog2.json()["overall_completion_percentage"] == 0.0


@pytest.mark.asyncio
async def test_duplicate_enrollment_conflict_prevention(async_client: AsyncClient, setup_security_fixtures):
    data = setup_security_fixtures
    course_a = data["course_a"]

    # Enroll Student 2
    res = await async_client.post(
        f"/api/v1/courses/{course_a.id}/enroll",
        headers={"Authorization": f"Bearer {data['student_2_token']}"},
    )
    assert res.status_code == 201

    # Duplicate enrollment attempt must be rejected with 400 or 409
    res_dup = await async_client.post(
        f"/api/v1/courses/{course_a.id}/enroll",
        headers={"Authorization": f"Bearer {data['student_2_token']}"},
    )
    assert res_dup.status_code in [400, 409]


@pytest.mark.asyncio
async def test_sensitive_credentials_not_exposed(async_client: AsyncClient, setup_security_fixtures):
    data = setup_security_fixtures

    # Auth profile endpoint must not return hashed_password
    res = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {data['student_1_token']}"},
    )
    assert res.status_code == 200
    res_body = res.json()
    assert "hashed_password" not in res_body
    assert "password" not in res_body
    assert "jwt_secret" not in res_body
