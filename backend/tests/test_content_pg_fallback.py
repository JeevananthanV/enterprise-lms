import pytest
import pytest_asyncio
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.db.mongodb import mongodb_manager
from app.models.user import User, UserRole
from app.models.course import Course, CourseStatus, CourseLevel
from app.models.module import CourseModule
from app.models.lesson import Lesson, LessonContentType
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.lesson_content import LessonContentPG
from app.core.security import create_access_token


@pytest_asyncio.fixture
async def disable_mongodb():
    """Explicitly disable MongoDB to force PostgreSQL fallback engine."""
    original_enabled = settings.MONGODB_ENABLED
    original_db = mongodb_manager.db
    settings.MONGODB_ENABLED = False
    mongodb_manager.db = None
    mongodb_manager.client = None

    yield

    settings.MONGODB_ENABLED = original_enabled
    mongodb_manager.db = original_db


@pytest_asyncio.fixture
async def fallback_test_data(db_session: AsyncSession):
    uid = uuid.uuid4().hex[:6]

    instructor = User(
        email=f"inst.fallback.{uid}@example.com",
        hashed_password="hashed_password",
        full_name="Fallback Instructor",
        role=UserRole.INSTRUCTOR,
        is_active=True,
    )
    student = User(
        email=f"student.fallback.{uid}@example.com",
        hashed_password="hashed_password",
        full_name="Fallback Student",
        role=UserRole.STUDENT,
        is_active=True,
    )

    db_session.add_all([instructor, student])
    await db_session.commit()
    await db_session.refresh(instructor)
    await db_session.refresh(student)

    course = Course(
        title=f"PostgreSQL Fallback Course {uid}",
        slug=f"pg-fallback-{uid}",
        description="Course running purely on PostgreSQL without MongoDB",
        instructor_id=instructor.id,
        level=CourseLevel.INTERMEDIATE,
        status=CourseStatus.PUBLISHED,
    )
    db_session.add(course)
    await db_session.commit()
    await db_session.refresh(course)

    module = CourseModule(
        course_id=course.id,
        title="Module 1: Relational Fallback",
        order_index=1,
    )
    db_session.add(module)
    await db_session.commit()
    await db_session.refresh(module)

    lesson = Lesson(
        module_id=module.id,
        title="Lesson 1: Zero MongoDB Execution",
        slug=f"zero-mongo-{uid}",
        content_type=LessonContentType.TEXT,
        order_index=1,
        is_free_preview=False,
    )
    db_session.add(lesson)
    await db_session.commit()
    await db_session.refresh(lesson)

    enrollment = Enrollment(
        user_id=student.id,
        course_id=course.id,
        status=EnrollmentStatus.ACTIVE,
    )
    db_session.add(enrollment)
    await db_session.commit()

    return {
        "instructor": instructor,
        "student": student,
        "course": course,
        "module": module,
        "lesson": lesson,
    }


def auth_header(user: User):
    token = create_access_token(
        subject=user.id,
        role=user.role.value,
        extra_claims={"email": user.email},
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_complete_lesson_content_crud_on_postgresql_fallback(
    async_client: AsyncClient, fallback_test_data, disable_mongodb, db_session: AsyncSession
):
    """Verify that lesson content create, read, update, publish, and unpublish work 100% on PostgreSQL when MongoDB is disabled."""
    data = fallback_test_data
    inst = data["instructor"]
    stud = data["student"]
    lesson = data["lesson"]

    # 1. Create content via API
    payload = {
        "content_type": "VIDEO",
        "body": "<h1>PostgreSQL Fallback Lesson Body</h1>",
        "video_metadata": {
            "video_url": "https://cdn.example.com/videos/fallback.mp4",
            "duration_seconds": 600,
            "resolution": "1080p",
            "provider": "cdn",
        },
        "pdf_metadata": {
            "file_url": "https://cdn.example.com/docs/slides.pdf",
            "file_name": "slides.pdf",
            "page_count": 12,
        },
        "transcript": {
            "language": "en",
            "content": "Transcript running through PostgreSQL JSON column",
            "format": "text",
        },
        "external_resources": [
            {
                "title": "PostgreSQL Documentation",
                "url": "https://www.postgresql.org/docs/",
                "resource_type": "docs",
            }
        ],
    }

    create_res = await async_client.post(
        f"/api/v1/lessons/{lesson.id}/content",
        json=payload,
        headers=auth_header(inst),
    )
    assert create_res.status_code == 201
    created_data = create_res.json()
    assert created_data["lesson_id"] == lesson.id
    assert created_data["version"] == 1
    assert created_data["is_published"] is False
    assert created_data["video_metadata"]["video_url"] == "https://cdn.example.com/videos/fallback.mp4"

    # Verify directly stored in lesson_contents_pg
    res = await db_session.execute(select(LessonContentPG).where(LessonContentPG.lesson_id == lesson.id))
    pg_content = res.scalars().first()
    assert pg_content is not None
    assert pg_content.body == "<h1>PostgreSQL Fallback Lesson Body</h1>"
    assert pg_content.version == 1

    # 2. Student cannot read unpublished content -> 403 Forbidden
    stud_read_unpub = await async_client.get(
        f"/api/v1/lessons/{lesson.id}/content",
        headers=auth_header(stud),
    )
    assert stud_read_unpub.status_code == 403

    # 3. Publish content
    pub_res = await async_client.post(
        f"/api/v1/lessons/{lesson.id}/content/publish",
        headers=auth_header(inst),
    )
    assert pub_res.status_code == 200
    assert pub_res.json()["is_published"] is True
    assert pub_res.json()["published_at"] is not None

    # 4. Enrolled student can now read published content -> 200 OK
    stud_read_pub = await async_client.get(
        f"/api/v1/lessons/{lesson.id}/content",
        headers=auth_header(stud),
    )
    assert stud_read_pub.status_code == 200
    assert stud_read_pub.json()["body"] == "<h1>PostgreSQL Fallback Lesson Body</h1>"

    # 5. Update content (version increments to 2)
    update_res = await async_client.put(
        f"/api/v1/lessons/{lesson.id}/content",
        json={"body": "<h2>Updated Revision 2 in PostgreSQL</h2>"},
        headers=auth_header(inst),
    )
    assert update_res.status_code == 200
    assert update_res.json()["version"] == 2
    assert update_res.json()["body"] == "<h2>Updated Revision 2 in PostgreSQL</h2>"

    # 6. Unpublish content
    unpub_res = await async_client.post(
        f"/api/v1/lessons/{lesson.id}/content/unpublish",
        headers=auth_header(inst),
    )
    assert unpub_res.status_code == 200
    assert unpub_res.json()["is_published"] is False


@pytest.mark.asyncio
async def test_health_check_when_mongodb_disabled(async_client: AsyncClient, disable_mongodb):
    """Verify that /health remains healthy when MongoDB is disabled."""
    res = await async_client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "optional" in data["subsystems"]["mongodb"].lower()
