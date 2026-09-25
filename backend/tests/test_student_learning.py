import pytest
import pytest_asyncio
import uuid
from httpx import AsyncClient
from app.models.user import User, UserRole
from app.models.course import Course, CourseStatus, CourseLevel
from app.models.module import CourseModule
from app.models.lesson import Lesson, LessonContentType
from app.models.quiz import Quiz, Question, Answer, QuestionType
from app.core.security import create_access_token


@pytest_asyncio.fixture
async def student1_headers(db_session):
    user = User(
        email=f"student1.{uuid.uuid4().hex[:6]}@example.com",
        hashed_password="hashedpassword123",
        full_name="Alice Student",
        role=UserRole.STUDENT,
    )
    db_session.add(user)
    await db_session.commit()
    token = create_access_token(subject=user.id, role=user.role.value, extra_claims={"email": user.email})
    return {"Authorization": f"Bearer {token}", "user_id": user.id, "email": user.email}


@pytest_asyncio.fixture
async def student2_headers(db_session):
    user = User(
        email=f"student2.{uuid.uuid4().hex[:6]}@example.com",
        hashed_password="hashedpassword123",
        full_name="Bob Student",
        role=UserRole.STUDENT,
    )
    db_session.add(user)
    await db_session.commit()
    token = create_access_token(subject=user.id, role=user.role.value, extra_claims={"email": user.email})
    return {"Authorization": f"Bearer {token}", "user_id": user.id, "email": user.email}


@pytest_asyncio.fixture
async def instructor_headers(db_session):
    user = User(
        email=f"instructor.{uuid.uuid4().hex[:6]}@example.com",
        hashed_password="hashedpassword123",
        full_name="Dr. Smith",
        role=UserRole.INSTRUCTOR,
    )
    db_session.add(user)
    await db_session.commit()
    token = create_access_token(subject=user.id, role=user.role.value, extra_claims={"email": user.email})
    return {"Authorization": f"Bearer {token}", "user_id": user.id, "email": user.email}


@pytest_asyncio.fixture
async def sample_published_course(db_session, instructor_headers):
    # Create published course with 2 modules, 2 lessons, and a quiz
    course = Course(
        instructor_id=instructor_headers["user_id"],
        title=f"Cloud Native Architectures {uuid.uuid4().hex[:4]}",
        slug=f"cloud-native-{uuid.uuid4().hex[:6]}",
        short_description="Learn Kubernetes and Microservices.",
        description="Comprehensive enterprise cloud architecture deep-dive syllabus.",
        category="Cloud & DevOps",
        level=CourseLevel.INTERMEDIATE,
        status=CourseStatus.PUBLISHED,
        estimated_duration_minutes=120,
    )
    db_session.add(course)
    await db_session.commit()

    module1 = CourseModule(
        course_id=course.id,
        title="Module 1: Foundations",
        order_index=1,
        is_published=True,
    )
    db_session.add(module1)
    await db_session.commit()

    lesson1 = Lesson(
        module_id=module1.id,
        title="Lesson 1: Intro to Containers",
        slug="l1-containers",
        content_type=LessonContentType.TEXT,
        content="Container fundamentals and Docker orchestration.",
        order_index=1,
        duration_minutes=20,
        is_published=True,
    )
    lesson2 = Lesson(
        module_id=module1.id,
        title="Lesson 2: Pod Networking",
        slug="l2-networking",
        content_type=LessonContentType.VIDEO,
        content="Deep dive into overlay networks.",
        order_index=2,
        duration_minutes=30,
        is_published=True,
    )
    db_session.add_all([lesson1, lesson2])
    await db_session.commit()

    # Create Quiz on lesson 2
    quiz = Quiz(
        course_id=course.id,
        lesson_id=lesson2.id,
        title="Pod Networking Knowledge Check",
        description="Verify your understanding of pod networking.",
        passing_score=70,
        max_attempts=3,
    )
    db_session.add(quiz)
    await db_session.commit()

    q1 = Question(
        quiz_id=quiz.id,
        question_text="Which component manages pod-to-pod communication in Kubernetes?",
        question_type=QuestionType.SINGLE_CHOICE,
        points=10,
        order_index=1,
    )
    db_session.add(q1)
    await db_session.commit()

    a1_correct = Answer(question_id=q1.id, answer_text="CNI Plugin", is_correct=True, order_index=1)
    a1_wrong = Answer(question_id=q1.id, answer_text="Kubelet", is_correct=False, order_index=2)
    db_session.add_all([a1_correct, a1_wrong])
    await db_session.commit()

    return {
        "course_id": course.id,
        "module1_id": module1.id,
        "lesson1_id": lesson1.id,
        "lesson2_id": lesson2.id,
        "quiz_id": quiz.id,
        "q1_id": q1.id,
        "a1_correct_id": a1_correct.id,
        "a1_wrong_id": a1_wrong.id,
    }


@pytest.mark.asyncio
async def test_student_enrollment_workflow(
    async_client: AsyncClient,
    student1_headers: dict,
    instructor_headers: dict,
    sample_published_course: dict,
):
    course_id = sample_published_course["course_id"]
    headers = {"Authorization": student1_headers["Authorization"]}

    # 1. Unauthenticated request rejected
    res = await async_client.post(f"/api/v1/courses/{course_id}/enroll")
    assert res.status_code == 401

    # 2. Non-student role rejected (Instructor)
    inst_headers = {"Authorization": instructor_headers["Authorization"]}
    res = await async_client.post(f"/api/v1/courses/{course_id}/enroll", headers=inst_headers)
    assert res.status_code == 403

    # 3. Invalid course ID -> 404
    res = await async_client.post("/api/v1/courses/invalid-uuid-999/enroll", headers=headers)
    assert res.status_code == 404

    # 4. Successful student enrollment
    res = await async_client.post(f"/api/v1/courses/{course_id}/enroll", headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["course_id"] == course_id
    assert data["user_id"] == student1_headers["user_id"]
    assert data["status"] == "ACTIVE"
    assert data["progress_percentage"] == 0.0

    # 5. Duplicate enrollment rejected -> 400 Bad Request
    res_dup = await async_client.post(f"/api/v1/courses/{course_id}/enroll", headers=headers)
    assert res_dup.status_code == 400
    assert "already enrolled" in res_dup.json()["detail"].lower()


@pytest.mark.asyncio
async def test_my_enrollments_and_course_player(
    async_client: AsyncClient,
    student1_headers: dict,
    sample_published_course: dict,
):
    course_id = sample_published_course["course_id"]
    headers = {"Authorization": student1_headers["Authorization"]}

    # Enroll in course
    await async_client.post(f"/api/v1/courses/{course_id}/enroll", headers=headers)

    # Fetch /api/v1/me/enrollments
    res = await async_client.get("/api/v1/me/enrollments", headers=headers)
    assert res.status_code == 200
    enrollments = res.json()
    assert len(enrollments) >= 1
    enrolled_c = next((e for e in enrollments if e["course_id"] == course_id), None)
    assert enrolled_c is not None
    assert enrolled_c["course"]["title"] is not None
    assert enrolled_c["total_lesson_count"] == 2
    assert enrolled_c["completed_lesson_count"] == 0

    # Fetch Course Player data
    player_res = await async_client.get(f"/api/v1/courses/{course_id}/player", headers=headers)
    assert player_res.status_code == 200
    player_data = player_res.json()
    assert player_data["course_id"] == course_id
    assert player_data["is_enrolled"] is True
    assert player_data["total_lessons"] == 2
    assert len(player_data["modules"]) == 1
    assert len(player_data["modules"][0]["lessons"]) == 2


@pytest.mark.asyncio
async def test_lesson_progress_idempotency_and_completion(
    async_client: AsyncClient,
    student1_headers: dict,
    student2_headers: dict,
    sample_published_course: dict,
):
    course_id = sample_published_course["course_id"]
    lesson1_id = sample_published_course["lesson1_id"]
    lesson2_id = sample_published_course["lesson2_id"]

    headers1 = {"Authorization": student1_headers["Authorization"]}
    headers2 = {"Authorization": student2_headers["Authorization"]}

    # Student 1 enrolls
    await async_client.post(f"/api/v1/courses/{course_id}/enroll", headers=headers1)

    # 1. Complete Lesson 1
    res1 = await async_client.post(
        f"/api/v1/lessons/{lesson1_id}/progress",
        json={"is_completed": True},
        headers=headers1,
    )
    assert res1.status_code == 200
    prog1 = res1.json()
    assert prog1["lesson_id"] == lesson1_id
    assert prog1["is_completed"] is True
    assert prog1["course_progress_percentage"] == 50.0

    # 2. Idempotent re-submission (marking again does not distort progress)
    res1_again = await async_client.post(
        f"/api/v1/lessons/{lesson1_id}/progress",
        json={"is_completed": True},
        headers=headers1,
    )
    assert res1_again.status_code == 200
    assert res1_again.json()["course_progress_percentage"] == 50.0

    # 3. Student 2 has not completed anything (cross-student isolation)
    # Student 2 enrolls
    await async_client.post(f"/api/v1/courses/{course_id}/enroll", headers=headers2)
    s2_enrollments = await async_client.get("/api/v1/me/enrollments", headers=headers2)
    s2_c = next((e for e in s2_enrollments.json() if e["course_id"] == course_id), None)
    assert s2_c["progress_percentage"] == 0.0

    # 4. Student 1 completes Lesson 2 -> course reaches 100% and marks COMPLETED
    res2 = await async_client.post(
        f"/api/v1/lessons/{lesson2_id}/progress",
        json={"is_completed": True},
        headers=headers1,
    )
    assert res2.status_code == 200
    assert res2.json()["course_progress_percentage"] == 100.0

    s1_enrollments = await async_client.get("/api/v1/me/enrollments", headers=headers1)
    s1_c = next((e for e in s1_enrollments.json() if e["course_id"] == course_id), None)
    assert s1_c["status"] == "COMPLETED"
    assert s1_c["progress_percentage"] == 100.0


@pytest.mark.asyncio
async def test_quiz_attempt_scoring_and_results(
    async_client: AsyncClient,
    student1_headers: dict,
    student2_headers: dict,
    sample_published_course: dict,
):
    course_id = sample_published_course["course_id"]
    quiz_id = sample_published_course["quiz_id"]
    q1_id = sample_published_course["q1_id"]
    a1_correct_id = sample_published_course["a1_correct_id"]
    a1_wrong_id = sample_published_course["a1_wrong_id"]

    headers1 = {"Authorization": student1_headers["Authorization"]}
    headers2 = {"Authorization": student2_headers["Authorization"]}

    # Enroll student 1
    await async_client.post(f"/api/v1/courses/{course_id}/enroll", headers=headers1)

    # 1. Fetch sanitized quiz -> correct answers must NOT be leaked
    quiz_res = await async_client.get(f"/api/v1/quizzes/{quiz_id}", headers=headers1)
    assert quiz_res.status_code == 200
    quiz_data = quiz_res.json()
    assert quiz_data["id"] == quiz_id
    assert len(quiz_data["questions"]) == 1
    # Verify no 'is_correct' field in any question answer choice
    for ans in quiz_data["questions"][0]["answers"]:
        assert "is_correct" not in ans

    # 2. Submit incorrect attempt
    wrong_sub = {
        "submissions": [
            {"question_id": q1_id, "selected_answer_ids": [a1_wrong_id]}
        ]
    }
    att_res1 = await async_client.post(
        f"/api/v1/quizzes/{quiz_id}/attempts",
        json=wrong_sub,
        headers=headers1,
    )
    assert att_res1.status_code == 201
    att1 = att_res1.json()
    assert att1["score"] == 0.0
    assert att1["passed"] is False

    # 3. Submit correct attempt
    correct_sub = {
        "submissions": [
            {"question_id": q1_id, "selected_answer_ids": [a1_correct_id]}
        ]
    }
    att_res2 = await async_client.post(
        f"/api/v1/quizzes/{quiz_id}/attempts",
        json=correct_sub,
        headers=headers1,
    )
    assert att_res2.status_code == 201
    att2 = att_res2.json()
    assert att2["score"] == 100.0
    assert att2["passed"] is True
    assert att2["lesson_completed"] is True

    # 4. Check results endpoint
    results_res = await async_client.get(f"/api/v1/quizzes/{quiz_id}/results", headers=headers1)
    assert results_res.status_code == 200
    results = results_res.json()
    assert len(results["attempts"]) == 2
    assert results["highest_score"] == 100.0
    assert results["has_passed"] is True

    # 5. Student 2 has 0 attempts on this quiz
    # Enroll student 2 first
    await async_client.post(f"/api/v1/courses/{course_id}/enroll", headers=headers2)
    s2_results = await async_client.get(f"/api/v1/quizzes/{quiz_id}/results", headers=headers2)
    assert s2_results.status_code == 200
    assert len(s2_results.json()["attempts"]) == 0
