import pytest
import pytest_asyncio
import uuid
from httpx import AsyncClient
from app.models.user import User, UserRole
from app.core.security import create_access_token


async def get_auth_headers(client: AsyncClient, email: str, role: UserRole, user_id: int) -> dict:
    token = create_access_token(subject=user_id, role=role.value, extra_claims={"email": email})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def instructor1_headers(db_session):
    user = User(
        email=f"inst1.{uuid.uuid4().hex[:6]}@example.com",
        hashed_password="hashedpassword123",
        full_name="Instructor Alpha",
        role=UserRole.INSTRUCTOR,
    )
    db_session.add(user)
    await db_session.commit()
    token = create_access_token(subject=user.id, role=user.role.value, extra_claims={"email": user.email})
    return {"Authorization": f"Bearer {token}", "user_id": user.id}


@pytest_asyncio.fixture
async def instructor2_headers(db_session):
    user = User(
        email=f"inst2.{uuid.uuid4().hex[:6]}@example.com",
        hashed_password="hashedpassword123",
        full_name="Instructor Beta",
        role=UserRole.INSTRUCTOR,
    )
    db_session.add(user)
    await db_session.commit()
    token = create_access_token(subject=user.id, role=user.role.value, extra_claims={"email": user.email})
    return {"Authorization": f"Bearer {token}", "user_id": user.id}


@pytest_asyncio.fixture
async def student_headers(db_session):
    user = User(
        email=f"student.{uuid.uuid4().hex[:6]}@example.com",
        hashed_password="hashedpassword123",
        full_name="Student Charlie",
        role=UserRole.STUDENT,
    )
    db_session.add(user)
    await db_session.commit()
    token = create_access_token(subject=user.id, role=user.role.value, extra_claims={"email": user.email})
    return {"Authorization": f"Bearer {token}", "user_id": user.id}


@pytest_asyncio.fixture
async def admin_headers(db_session):
    user = User(
        email=f"admin.{uuid.uuid4().hex[:6]}@example.com",
        hashed_password="hashedpassword123",
        full_name="Admin Overlord",
        role=UserRole.PLATFORM_ADMIN,
    )
    db_session.add(user)
    await db_session.commit()
    token = create_access_token(subject=user.id, role=user.role.value, extra_claims={"email": user.email})
    return {"Authorization": f"Bearer {token}", "user_id": user.id}


@pytest.mark.asyncio
async def test_instructor_course_lifecycle_and_ownership(
    async_client: AsyncClient,
    instructor1_headers: dict,
    instructor2_headers: dict,
    student_headers: dict,
    admin_headers: dict,
):
    inst1_auth = {"Authorization": instructor1_headers["Authorization"]}
    inst2_auth = {"Authorization": instructor2_headers["Authorization"]}
    stud_auth = {"Authorization": student_headers["Authorization"]}
    admin_auth = {"Authorization": admin_headers["Authorization"]}

    # 1. Student cannot create a course (403)
    resp = await async_client.post(
        "/api/v1/instructor/courses",
        headers=stud_auth,
        json={"title": "Unauthorized Student Course", "category": "Engineering"},
    )
    assert resp.status_code == 403

    # 2. Instructor 1 creates a course (201, status = DRAFT)
    course_data = {
        "title": "Scalable Microservices with Go",
        "short_description": "Learn high-throughput distributed microservices.",
        "description": "Comprehensive guide to developing, benchmarking, and scaling microservices.",
        "category": "Cloud & DevOps",
        "level": "ADVANCED",
        "price": 149.99,
        "estimated_duration_minutes": 180,
    }
    resp = await async_client.post(
        "/api/v1/instructor/courses",
        headers=inst1_auth,
        json=course_data,
    )
    assert resp.status_code == 201
    course = resp.json()
    course_id = course["id"]
    assert course["title"] == "Scalable Microservices with Go"
    assert course["status"] == "DRAFT"
    assert course["instructor_id"] == instructor1_headers["user_id"]

    # 3. Instructor 1 can retrieve and edit own course
    resp = await async_client.get(f"/api/v1/instructor/courses/{course_id}", headers=inst1_auth)
    assert resp.status_code == 200

    resp = await async_client.patch(
        f"/api/v1/instructor/courses/{course_id}",
        headers=inst1_auth,
        json={"price": 129.99},
    )
    assert resp.status_code == 200
    assert resp.json()["price"] == 129.99

    # 4. Cross-Instructor Ownership Isolation: Instructor 2 cannot edit or delete Instructor 1's course
    resp = await async_client.patch(
        f"/api/v1/instructor/courses/{course_id}",
        headers=inst2_auth,
        json={"title": "Hacked Course Title"},
    )
    assert resp.status_code == 403

    resp = await async_client.delete(f"/api/v1/instructor/courses/{course_id}", headers=inst2_auth)
    assert resp.status_code == 403

    # 5. Publishing Validation: Attempting to publish without modules & lessons fails (400)
    resp = await async_client.post(f"/api/v1/instructor/courses/{course_id}/publish", headers=inst1_auth)
    assert resp.status_code == 400
    assert "Course must have at least one module" in str(resp.json())

    # 6. Add Module and Lessons
    resp_mod1 = await async_client.post(
        f"/api/v1/instructor/courses/{course_id}/modules",
        headers=inst1_auth,
        json={"title": "Module 1: Concurrency Primitives", "order_index": 1},
    )
    assert resp_mod1.status_code == 201
    mod1_id = resp_mod1.json()["id"]

    resp_mod2 = await async_client.post(
        f"/api/v1/instructor/courses/{course_id}/modules",
        headers=inst1_auth,
        json={"title": "Module 2: gRPC & Protobuf", "order_index": 2},
    )
    assert resp_mod2.status_code == 201
    mod2_id = resp_mod2.json()["id"]

    # Instructor 2 cannot add lessons to Instructor 1's module
    resp = await async_client.post(
        f"/api/v1/instructor/modules/{mod1_id}/lessons",
        headers=inst2_auth,
        json={"title": "Malicious Lesson"},
    )
    assert resp.status_code == 403

    # Instructor 1 adds lessons
    resp_les1 = await async_client.post(
        f"/api/v1/instructor/modules/{mod1_id}/lessons",
        headers=inst1_auth,
        json={
            "title": "Goroutines and Channels",
            "content_type": "TEXT",
            "duration_minutes": 25,
            "order_index": 1,
            "is_free_preview": True,
        },
    )
    assert resp_les1.status_code == 201
    les1_id = resp_les1.json()["id"]

    resp_les2 = await async_client.post(
        f"/api/v1/instructor/modules/{mod1_id}/lessons",
        headers=inst1_auth,
        json={
            "title": "Sync Package and Mutexes",
            "content_type": "TEXT",
            "duration_minutes": 30,
            "order_index": 2,
        },
    )
    assert resp_les2.status_code == 201
    les2_id = resp_les2.json()["id"]

    # 7. Reorder Modules and Lessons
    resp_reorder_mods = await async_client.post(
        f"/api/v1/instructor/courses/{course_id}/modules/reorder",
        headers=inst1_auth,
        json={"module_ids": [mod2_id, mod1_id]},
    )
    assert resp_reorder_mods.status_code == 200
    reordered_mods = resp_reorder_mods.json()
    assert reordered_mods[0]["id"] == mod2_id
    assert reordered_mods[0]["order_index"] == 1
    assert reordered_mods[1]["id"] == mod1_id
    assert reordered_mods[1]["order_index"] == 2

    resp_reorder_les = await async_client.post(
        f"/api/v1/instructor/modules/{mod1_id}/lessons/reorder",
        headers=inst1_auth,
        json={"lesson_ids": [les2_id, les1_id]},
    )
    assert resp_reorder_les.status_code == 200
    reordered_les = resp_reorder_les.json()
    assert reordered_les[0]["id"] == les2_id
    assert reordered_les[0]["order_index"] == 1

    # 8. Draft is hidden from public course catalog
    resp_catalog = await async_client.get("/api/v1/courses")
    assert resp_catalog.status_code == 200
    catalog_items = resp_catalog.json()["items"]
    assert all(c["id"] != course_id for c in catalog_items)

    # 9. Instructor 1 publishes the course
    resp_pub = await async_client.post(f"/api/v1/instructor/courses/{course_id}/publish", headers=inst1_auth)
    assert resp_pub.status_code == 200
    assert resp_pub.json()["status"] == "PUBLISHED"

    # 10. Published course is now visible in public course catalog
    resp_catalog = await async_client.get("/api/v1/courses")
    assert resp_catalog.status_code == 200
    catalog_items = resp_catalog.json()["items"]
    matching = [c for c in catalog_items if c["id"] == course_id]
    assert len(matching) == 1
    assert matching[0]["title"] == "Scalable Microservices with Go"

    # 11. Search and Filtering in Catalog
    resp_search = await async_client.get("/api/v1/courses?search=Microservices")
    assert resp_search.status_code == 200
    assert len(resp_search.json()["items"]) >= 1

    resp_filter_cat = await async_client.get("/api/v1/courses?category=Cloud%20%26%20DevOps")
    assert resp_filter_cat.status_code == 200
    assert any(c["id"] == course_id for c in resp_filter_cat.json()["items"])

    resp_filter_level = await async_client.get("/api/v1/courses?level=ADVANCED")
    assert resp_filter_level.status_code == 200
    assert any(c["id"] == course_id for c in resp_filter_level.json()["items"])

    # 12. Public Course Details & Curriculum
    resp_details = await async_client.get(f"/api/v1/courses/{course_id}")
    assert resp_details.status_code == 200
    assert resp_details.json()["title"] == "Scalable Microservices with Go"

    resp_curr = await async_client.get(f"/api/v1/courses/{course_id}/curriculum")
    assert resp_curr.status_code == 200
    assert len(resp_curr.json()) == 2

    # 13. Unpublish removes course from catalog
    resp_unpub = await async_client.post(f"/api/v1/instructor/courses/{course_id}/unpublish", headers=inst1_auth)
    assert resp_unpub.status_code == 200
    assert resp_unpub.json()["status"] == "UNPUBLISHED"

    resp_catalog_after = await async_client.get("/api/v1/courses")
    assert all(c["id"] != course_id for c in resp_catalog_after.json()["items"])

    # 14. Admin has global management authority
    resp_admin_preview = await async_client.get(f"/api/v1/instructor/courses/{course_id}/preview", headers=admin_auth)
    assert resp_admin_preview.status_code == 200
