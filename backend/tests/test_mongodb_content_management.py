import pytest
import pytest_asyncio
import uuid
from bson import ObjectId
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.mongodb import mongodb_manager
from app.models.user import User, UserRole
from app.models.course import Course, CourseStatus, CourseLevel
from app.models.module import CourseModule
from app.models.lesson import Lesson, LessonContentType
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.core.security import create_access_token


class MockInsertOneResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id


class MockDeleteResult:
    def __init__(self, deleted_count):
        self.deleted_count = deleted_count


class MockAsyncCollection:
    def __init__(self):
        self.docs: Dict[str, Dict[str, Any]] = {}

    def _matches(self, doc: Dict[str, Any], filter_dict: Dict[str, Any]) -> bool:
        if "$or" in filter_dict:
            return any(self._matches(doc, cond) for cond in filter_dict["$or"])
        for k, v in filter_dict.items():
            if k == "_id":
                if str(doc.get("_id")) != str(v):
                    return False
            elif doc.get(k) != v:
                return False
        return True

    async def find_one(self, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for doc in self.docs.values():
            if self._matches(doc, filter_dict):
                return dict(doc)
        return None

    async def insert_one(self, doc: Dict[str, Any]) -> MockInsertOneResult:
        doc_copy = dict(doc)
        if "_id" not in doc_copy:
            doc_copy["_id"] = ObjectId()
        doc_id = str(doc_copy["_id"])
        self.docs[doc_id] = doc_copy
        return MockInsertOneResult(doc_copy["_id"])

    async def find_one_and_update(
        self,
        filter_dict: Dict[str, Any],
        update_dict: Dict[str, Any],
        return_document: bool = True,
    ) -> Optional[Dict[str, Any]]:
        for doc_id, doc in self.docs.items():
            if self._matches(doc, filter_dict):
                if "$set" in update_dict:
                    doc.update(update_dict["$set"])
                if "$inc" in update_dict:
                    for k, v in update_dict["$inc"].items():
                        doc[k] = doc.get(k, 0) + v
                self.docs[doc_id] = doc
                return dict(doc)
        return None

    async def delete_one(self, filter_dict: Dict[str, Any]) -> MockDeleteResult:
        for doc_id, doc in list(self.docs.items()):
            if self._matches(doc, filter_dict):
                del self.docs[doc_id]
                return MockDeleteResult(1)
        return MockDeleteResult(0)

    async def create_indexes(self, indexes: List[Any]) -> List[str]:
        return ["index_created"]


class MockAsyncDatabase:
    def __init__(self):
        self.collections: Dict[str, MockAsyncCollection] = {
            "lesson_contents": MockAsyncCollection()
        }

    def __getitem__(self, name: str) -> MockAsyncCollection:
        if name not in self.collections:
            self.collections[name] = MockAsyncCollection()
        return self.collections[name]


@pytest_asyncio.fixture(autouse=True)
async def setup_mongodb_mock():
    """Ensure an isolated in-memory MongoDB collection for every test."""
    from app.core.config import settings
    mock_db = MockAsyncDatabase()
    original_db = mongodb_manager.db
    original_connected = mongodb_manager.is_connected
    original_enabled = settings.MONGODB_ENABLED
    mongodb_manager.db = mock_db
    mongodb_manager.is_connected = True
    settings.MONGODB_ENABLED = True
    yield mock_db
    mongodb_manager.db = original_db
    mongodb_manager.is_connected = original_connected
    settings.MONGODB_ENABLED = original_enabled


@pytest_asyncio.fixture
async def content_test_data(db_session: AsyncSession):
    """Seed users, course, modules, lessons and enrollments for content management testing."""
    uid = uuid.uuid4().hex[:6]

    # Instructors
    inst1 = User(
        email=f"instructor1.{uid}@example.com",
        hashed_password="hashed_password",
        full_name="Alice Instructor",
        role=UserRole.INSTRUCTOR,
        is_active=True,
    )
    inst2 = User(
        email=f"instructor2.{uid}@example.com",
        hashed_password="hashed_password",
        full_name="Bob Instructor",
        role=UserRole.INSTRUCTOR,
        is_active=True,
    )
    # Admin
    admin = User(
        email=f"admin.{uid}@example.com",
        hashed_password="hashed_password",
        full_name="Platform Admin",
        role=UserRole.PLATFORM_ADMIN,
        is_active=True,
    )
    # Students
    student1 = User(
        email=f"student1.{uid}@example.com",
        hashed_password="hashed_password",
        full_name="Charlie Student",
        role=UserRole.STUDENT,
        is_active=True,
    )
    student2 = User(
        email=f"student2.{uid}@example.com",
        hashed_password="hashed_password",
        full_name="Diana Student",
        role=UserRole.STUDENT,
        is_active=True,
    )

    db_session.add_all([inst1, inst2, admin, student1, student2])
    await db_session.commit()
    await db_session.refresh(inst1)
    await db_session.refresh(inst2)
    await db_session.refresh(admin)
    await db_session.refresh(student1)
    await db_session.refresh(student2)

    # Course owned by inst1
    course = Course(
        title=f"MongoDB Architecture {uid}",
        slug=f"mongodb-arch-{uid}",
        description="Master enterprise content management with MongoDB and PostgreSQL",
        instructor_id=inst1.id,
        level=CourseLevel.ADVANCED,
        status=CourseStatus.PUBLISHED,
    )
    db_session.add(course)
    await db_session.commit()
    await db_session.refresh(course)

    # Module
    module = CourseModule(
        course_id=course.id,
        title="Module 1: Document Modeling",
        order_index=1,
    )
    db_session.add(module)
    await db_session.commit()
    await db_session.refresh(module)

    # Regular lesson
    lesson1 = Lesson(
        module_id=module.id,
        title="Lesson 1: Introduction to Hybrid Content Storage",
        slug=f"intro-hybrid-content-{uid}",
        content_type=LessonContentType.TEXT,
        order_index=1,
        is_free_preview=False,
    )
    # Free preview lesson
    lesson_preview = Lesson(
        module_id=module.id,
        title="Lesson 2: Free Architecture Overview",
        slug=f"free-arch-overview-{uid}",
        content_type=LessonContentType.VIDEO,
        order_index=2,
        is_free_preview=True,
    )
    db_session.add_all([lesson1, lesson_preview])
    await db_session.commit()
    await db_session.refresh(lesson1)
    await db_session.refresh(lesson_preview)

    # Enroll student1 in the course
    enrollment = Enrollment(
        user_id=student1.id,
        course_id=course.id,
        status=EnrollmentStatus.ACTIVE,
    )
    db_session.add(enrollment)
    await db_session.commit()

    return {
        "inst1": inst1,
        "inst2": inst2,
        "admin": admin,
        "student1": student1,
        "student2": student2,
        "course": course,
        "module": module,
        "lesson1": lesson1,
        "lesson_preview": lesson_preview,
    }


def auth_header(user: User) -> Dict[str, str]:
    token = create_access_token(
        subject=user.id,
        role=user.role.value,
        extra_claims={"email": user.email},
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_lesson_content_as_course_instructor(
    async_client: AsyncClient, content_test_data, db_session: AsyncSession
):
    inst1 = content_test_data["inst1"]
    lesson1 = content_test_data["lesson1"]

    payload = {
        "content_type": "VIDEO",
        "body": "# Video Lesson Guide\n\nWelcome to this masterclass on multi-model databases.",
        "video_metadata": {
            "video_url": "s3://enterprise-lms-media/courses/mod1/lesson1.mp4",
            "duration_seconds": 940,
            "resolution": "1080p",
            "provider": "s3",
            "captions_url": "s3://enterprise-lms-media/courses/mod1/lesson1.vtt",
            "thumbnail_url": "https://cdn.example.com/thumbnails/lesson1.jpg",
        },
        "transcript": {
            "language": "en",
            "content": "00:00:00 Welcome to the lesson on MongoDB content storage...",
            "format": "vtt",
        },
        "external_resources": [
            {
                "title": "MongoDB Schema Design Documentation",
                "url": "https://www.mongodb.com/docs/manual/data-modeling/",
                "resource_type": "documentation",
                "description": "Official design patterns and antipatterns",
            }
        ],
        "custom_properties": {"estimated_reading_time_minutes": 15},
    }

    response = await async_client.post(
        f"/api/v1/lessons/{lesson1.id}/content",
        json=payload,
        headers=auth_header(inst1),
    )

    assert response.status_code == 201
    data = response.json()
    assert data["lesson_id"] == lesson1.id
    assert data["content_type"] == "VIDEO"
    assert data["video_metadata"]["video_url"] == "s3://enterprise-lms-media/courses/mod1/lesson1.mp4"
    assert data["video_metadata"]["duration_seconds"] == 940
    assert data["version"] == 1
    assert data["is_published"] is False
    assert len(data["external_resources"]) == 1

    # Verify PostgreSQL lesson has content_ref updated
    await db_session.refresh(lesson1)
    assert lesson1.content_ref == data["id"]


@pytest.mark.asyncio
async def test_create_content_duplicate_error(
    async_client: AsyncClient, content_test_data
):
    inst1 = content_test_data["inst1"]
    lesson1 = content_test_data["lesson1"]

    payload = {
        "content_type": "TEXT",
        "body": "Initial lesson body text",
    }

    # 1st creation succeeds
    res1 = await async_client.post(
        f"/api/v1/lessons/{lesson1.id}/content",
        json=payload,
        headers=auth_header(inst1),
    )
    assert res1.status_code == 201

    # 2nd creation fails with 400 Bad Request
    res2 = await async_client.post(
        f"/api/v1/lessons/{lesson1.id}/content",
        json=payload,
        headers=auth_header(inst1),
    )
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


@pytest.mark.asyncio
async def test_create_content_forbidden_for_other_instructor_and_students(
    async_client: AsyncClient, content_test_data
):
    inst2 = content_test_data["inst2"]
    student1 = content_test_data["student1"]
    lesson1 = content_test_data["lesson1"]

    payload = {"content_type": "TEXT", "body": "Unauthorized creation attempt"}

    # Other instructor attempting to create content for inst1's course
    res_inst2 = await async_client.post(
        f"/api/v1/lessons/{lesson1.id}/content",
        json=payload,
        headers=auth_header(inst2),
    )
    assert res_inst2.status_code == 403

    # Student attempting to create content
    res_student = await async_client.post(
        f"/api/v1/lessons/{lesson1.id}/content",
        json=payload,
        headers=auth_header(student1),
    )
    assert res_student.status_code == 403


@pytest.mark.asyncio
async def test_student_content_access_published_vs_unpublished(
    async_client: AsyncClient, content_test_data
):
    inst1 = content_test_data["inst1"]
    student1 = content_test_data["student1"]  # Enrolled
    student2 = content_test_data["student2"]  # Not enrolled
    lesson1 = content_test_data["lesson1"]

    # 1. Instructor creates content (starts as unpublished)
    create_payload = {
        "content_type": "TEXT",
        "body": "Secret unpublished course content",
    }
    await async_client.post(
        f"/api/v1/lessons/{lesson1.id}/content",
        json=create_payload,
        headers=auth_header(inst1),
    )

    # 2. Enrolled student tries to read unpublished content -> 403 Forbidden
    res_unpublished = await async_client.get(
        f"/api/v1/lessons/{lesson1.id}/content",
        headers=auth_header(student1),
    )
    assert res_unpublished.status_code == 403
    assert "not been published" in res_unpublished.json()["detail"]

    # 3. Instructor can read own unpublished content
    res_inst_read = await async_client.get(
        f"/api/v1/lessons/{lesson1.id}/content",
        headers=auth_header(inst1),
    )
    assert res_inst_read.status_code == 200
    assert res_inst_read.json()["is_published"] is False

    # 4. Instructor publishes content
    pub_res = await async_client.post(
        f"/api/v1/lessons/{lesson1.id}/content/publish",
        headers=auth_header(inst1),
    )
    assert pub_res.status_code == 200
    assert pub_res.json()["is_published"] is True
    assert pub_res.json()["published_at"] is not None

    # 5. Enrolled student can now read published content -> 200 OK
    res_student1 = await async_client.get(
        f"/api/v1/lessons/{lesson1.id}/content",
        headers=auth_header(student1),
    )
    assert res_student1.status_code == 200
    assert res_student1.json()["body"] == "Secret unpublished course content"

    # 6. Non-enrolled student tries to read non-preview lesson -> 403 Forbidden
    res_student2 = await async_client.get(
        f"/api/v1/lessons/{lesson1.id}/content",
        headers=auth_header(student2),
    )
    assert res_student2.status_code == 403
    assert "enrolled" in res_student2.json()["detail"]


@pytest.mark.asyncio
async def test_update_and_versioning_and_unpublish_flow(
    async_client: AsyncClient, content_test_data
):
    inst1 = content_test_data["inst1"]
    admin = content_test_data["admin"]
    student1 = content_test_data["student1"]
    lesson1 = content_test_data["lesson1"]

    # Create initial content
    await async_client.post(
        f"/api/v1/lessons/{lesson1.id}/content",
        json={"content_type": "TEXT", "body": "Version 1 content"},
        headers=auth_header(inst1),
    )

    # Publish
    await async_client.post(
        f"/api/v1/lessons/{lesson1.id}/content/publish",
        headers=auth_header(inst1),
    )

    # Update content (version increments to 2)
    update_payload = {
        "body": "Version 2 updated content with rich explanations",
        "pdf_metadata": {
            "file_url": "s3://enterprise-lms-media/docs/cheat-sheet.pdf",
            "file_name": "MongoDB-CheatSheet.pdf",
            "file_size_bytes": 1048576,
            "page_count": 4,
            "downloadable": True,
        },
    }
    update_res = await async_client.put(
        f"/api/v1/lessons/{lesson1.id}/content",
        json=update_payload,
        headers=auth_header(inst1),
    )
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["version"] == 2
    assert data["body"] == "Version 2 updated content with rich explanations"
    assert data["pdf_metadata"]["file_name"] == "MongoDB-CheatSheet.pdf"

    # Unpublish content
    unpub_res = await async_client.post(
        f"/api/v1/lessons/{lesson1.id}/content/unpublish",
        headers=auth_header(inst1),
    )
    assert unpub_res.status_code == 200
    assert unpub_res.json()["is_published"] is False
    assert unpub_res.json()["published_at"] is None

    # Student cannot read unpublished content
    student_res = await async_client.get(
        f"/api/v1/lessons/{lesson1.id}/content",
        headers=auth_header(student1),
    )
    assert student_res.status_code == 403

    # Platform Admin can read unpublished content
    admin_res = await async_client.get(
        f"/api/v1/lessons/{lesson1.id}/content",
        headers=auth_header(admin),
    )
    assert admin_res.status_code == 200
    assert admin_res.json()["version"] == 2


@pytest.mark.asyncio
async def test_student_free_preview_access(
    async_client: AsyncClient, content_test_data
):
    inst1 = content_test_data["inst1"]
    student2 = content_test_data["student2"]  # Not enrolled
    lesson_preview = content_test_data["lesson_preview"]  # is_free_preview=True

    # Create and publish content for preview lesson
    await async_client.post(
        f"/api/v1/lessons/{lesson_preview.id}/content",
        json={
            "content_type": "VIDEO",
            "video_metadata": {
                "video_url": "https://cdn.example.com/free-preview.mp4",
                "duration_seconds": 300,
                "provider": "cdn",
            },
        },
        headers=auth_header(inst1),
    )
    await async_client.post(
        f"/api/v1/lessons/{lesson_preview.id}/content/publish",
        headers=auth_header(inst1),
    )

    # Non-enrolled student can access free preview content
    response = await async_client.get(
        f"/api/v1/lessons/{lesson_preview.id}/content",
        headers=auth_header(student2),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["video_metadata"]["video_url"] == "https://cdn.example.com/free-preview.mp4"
