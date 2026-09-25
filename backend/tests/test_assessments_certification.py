import pytest
import pytest_asyncio
import uuid
from httpx import AsyncClient
from datetime import datetime, timezone, timedelta

from app.core.security import create_access_token
from app.models.user import User, UserRole
from app.models.course import Course, CourseStatus, CourseLevel
from app.models.module import CourseModule
from app.models.lesson import Lesson, LessonContentType
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.progress import LessonProgress
from app.models.quiz import Quiz, Question, Answer, QuestionType, QuizAttempt
from app.models.assignment import Assignment, AssignmentSubmission, SubmissionStatus
from app.models.certificate import Certificate


@pytest_asyncio.fixture
async def setup_phase6_data(db_session):
    # 1. Users
    inst1 = User(
        email=f"inst1.{uuid.uuid4().hex[:6]}@lms.local",
        full_name="Instructor Alpha",
        hashed_password="hashed_pw_test",
        role=UserRole.INSTRUCTOR,
        is_active=True,
    )
    inst2 = User(
        email=f"inst2.{uuid.uuid4().hex[:6]}@lms.local",
        full_name="Instructor Beta",
        hashed_password="hashed_pw_test",
        role=UserRole.INSTRUCTOR,
        is_active=True,
    )
    student1 = User(
        email=f"stud1.{uuid.uuid4().hex[:6]}@lms.local",
        full_name="Student One",
        hashed_password="hashed_pw_test",
        role=UserRole.STUDENT,
        is_active=True,
    )
    student2 = User(
        email=f"stud2.{uuid.uuid4().hex[:6]}@lms.local",
        full_name="Student Two",
        hashed_password="hashed_pw_test",
        role=UserRole.STUDENT,
        is_active=True,
    )
    db_session.add_all([inst1, inst2, student1, student2])
    await db_session.commit()
    await db_session.refresh(inst1)
    await db_session.refresh(inst2)
    await db_session.refresh(student1)
    await db_session.refresh(student2)

    inst1_token = create_access_token(subject=inst1.id, role=inst1.role.value, extra_claims={"email": inst1.email})
    inst2_token = create_access_token(subject=inst2.id, role=inst2.role.value, extra_claims={"email": inst2.email})
    student1_token = create_access_token(subject=student1.id, role=student1.role.value, extra_claims={"email": student1.email})
    student2_token = create_access_token(subject=student2.id, role=student2.role.value, extra_claims={"email": student2.email})

    # 2. Courses
    course1 = Course(
        id=str(uuid.uuid4()),
        title="Enterprise Cloud Architecture",
        slug=f"enterprise-cloud-arch-{uuid.uuid4().hex[:6]}",
        short_description="Cloud architecture curriculum",
        description="Deep dive into enterprise cloud architectures",
        category="Cloud",
        status=CourseStatus.PUBLISHED,
        level=CourseLevel.ADVANCED,
        instructor_id=inst1.id,
    )
    course2 = Course(
        id=str(uuid.uuid4()),
        title="Advanced Cyber Defense",
        slug=f"advanced-cyber-def-{uuid.uuid4().hex[:6]}",
        short_description="Cyber security curriculum",
        description="Enterprise security and monitoring",
        category="Security",
        status=CourseStatus.PUBLISHED,
        level=CourseLevel.ADVANCED,
        instructor_id=inst2.id,
    )
    db_session.add_all([course1, course2])
    await db_session.commit()
    await db_session.refresh(course1)
    await db_session.refresh(course2)

    # 3. Module & Lesson for Course 1
    mod1 = CourseModule(
        id=str(uuid.uuid4()),
        course_id=course1.id,
        title="Module 1: Foundations",
        order_index=1,
    )
    db_session.add(mod1)
    await db_session.commit()
    await db_session.refresh(mod1)

    les1 = Lesson(
        id=str(uuid.uuid4()),
        module_id=mod1.id,
        title="Lesson 1: Intro",
        slug="lesson-1-intro",
        content_type=LessonContentType.TEXT,
        order_index=1,
        is_published=True,
    )
    db_session.add(les1)
    await db_session.commit()
    await db_session.refresh(les1)

    # 4. Enrollments
    enroll1 = Enrollment(
        id=str(uuid.uuid4()),
        user_id=student1.id,
        course_id=course1.id,
        status=EnrollmentStatus.ACTIVE,
        progress_percentage=0.0,
    )
    db_session.add(enroll1)
    await db_session.commit()

    # 5. Quiz for Course 1
    quiz1 = Quiz(
        id=str(uuid.uuid4()),
        course_id=course1.id,
        lesson_id=les1.id,
        title="Cloud Architecture Quiz",
        passing_score=70,
        time_limit_minutes=10,
        max_attempts=2,
        randomize_questions=True,
    )
    db_session.add(quiz1)
    await db_session.commit()
    await db_session.refresh(quiz1)

    # Question & Answers
    q1 = Question(
        id=str(uuid.uuid4()),
        quiz_id=quiz1.id,
        question_text="What is high availability?",
        question_type=QuestionType.SINGLE_CHOICE,
        points=10,
        order_index=1,
    )
    db_session.add(q1)
    await db_session.commit()
    await db_session.refresh(q1)

    a1_1 = Answer(id=str(uuid.uuid4()), question_id=q1.id, answer_text="System uptime and resilience", is_correct=True, order_index=1)
    a1_2 = Answer(id=str(uuid.uuid4()), question_id=q1.id, answer_text="Single point of failure", is_correct=False, order_index=2)
    db_session.add_all([a1_1, a1_2])
    await db_session.commit()
    await db_session.refresh(a1_1)
    await db_session.refresh(a1_2)

    return {
        "inst1_headers": {"Authorization": f"Bearer {inst1_token}"},
        "inst2_headers": {"Authorization": f"Bearer {inst2_token}"},
        "student1_headers": {"Authorization": f"Bearer {student1_token}"},
        "student2_headers": {"Authorization": f"Bearer {student2_token}"},
        "course1_id": course1.id,
        "course2_id": course2.id,
        "lesson1_id": les1.id,
        "quiz1_id": quiz1.id,
        "question1_id": q1.id,
        "correct_ans1_id": a1_1.id,
        "wrong_ans1_id": a1_2.id,
        "student1_name": student1.full_name,
        "course1_title": course1.title,
    }


@pytest.mark.asyncio
async def test_assignment_lifecycle_and_ownership_isolation(async_client, setup_phase6_data):
    data = setup_phase6_data
    course1_id = data["course1_id"]

    # 1. Instructor 1 creates assignment on Course 1
    resp = await async_client.post(
        f"/api/v1/instructor/courses/{course1_id}/assignments",
        json={
            "course_id": course1_id,
            "title": "Cloud Infrastructure Capstone",
            "description": "Design a resilient multi-tier topology on AWS/GCP.",
            "max_marks": 100,
            "allowed_file_types": "pdf,zip",
            "max_file_size_mb": 15,
        },
        headers=data["inst1_headers"],
    )
    assert resp.status_code == 200
    assignment = resp.json()
    assignment_id = assignment["id"]
    assert assignment["title"] == "Cloud Infrastructure Capstone"
    assert assignment["max_marks"] == 100

    # 2. Instructor 2 CANNOT create assignment on Course 1 (Ownership check)
    resp = await async_client.post(
        f"/api/v1/instructor/courses/{course1_id}/assignments",
        json={
            "course_id": course1_id,
            "title": "Malicious Assignment",
            "max_marks": 50,
        },
        headers=data["inst2_headers"],
    )
    assert resp.status_code == 403

    # 3. Student submits assignment
    resp = await async_client.post(
        f"/api/v1/assignments/{assignment_id}/submissions",
        json={
            "submission_text": "Topology design completed with Terraform modules.",
            "file_url": "/api/v1/assignments/submissions/files/arch_design.pdf",
            "file_name": "arch_design.pdf",
            "file_size_bytes": 102400,
        },
        headers=data["student1_headers"],
    )
    assert resp.status_code == 200
    sub_data = resp.json()
    submission_id = sub_data["id"]
    assert sub_data["status"] == "SUBMITTED"

    # 4. Student views their own submission
    resp = await async_client.get(
        f"/api/v1/assignments/{assignment_id}/submissions/me",
        headers=data["student1_headers"],
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == submission_id

    # 5. Instructor 2 CANNOT view Instructor 1's assignment submissions
    resp = await async_client.get(
        f"/api/v1/instructor/assignments/{assignment_id}/submissions",
        headers=data["inst2_headers"],
    )
    assert resp.status_code == 403

    # 6. Instructor 2 CANNOT grade Instructor 1's submission
    resp = await async_client.post(
        f"/api/v1/instructor/submissions/{submission_id}/grade",
        json={"score": 95.0, "feedback": "Great work!"},
        headers=data["inst2_headers"],
    )
    assert resp.status_code == 403

    # 7. Instructor 1 grades the submission successfully
    resp = await async_client.post(
        f"/api/v1/instructor/submissions/{submission_id}/grade",
        json={"score": 95.0, "feedback": "Superb architectural design and modularization."},
        headers=data["inst1_headers"],
    )
    assert resp.status_code == 200
    graded = resp.json()
    assert graded["status"] == "GRADED"
    assert graded["score"] == 95.0
    assert "Superb" in graded["feedback"]

    # 8. Score exceeding max marks is rejected (400)
    resp = await async_client.post(
        f"/api/v1/instructor/submissions/{submission_id}/grade",
        json={"score": 150.0, "feedback": "Invalid score"},
        headers=data["inst1_headers"],
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_timed_and_randomized_quiz_engine(async_client, setup_phase6_data):
    data = setup_phase6_data
    quiz_id = data["quiz1_id"]
    question_id = data["question1_id"]
    correct_ans_id = data["correct_ans1_id"]

    # 1. Start timed quiz attempt
    resp = await async_client.post(
        f"/api/v1/quizzes/{quiz_id}/attempts/start",
        headers=data["student1_headers"],
    )
    assert resp.status_code == 201
    attempt_data = resp.json()
    attempt_id = attempt_data["attempt_id"]
    assert attempt_data["attempt_number"] == 1
    assert attempt_data["time_limit_minutes"] == 10
    assert attempt_data["expires_at"] is not None
    assert len(attempt_data["questions"]) == 1

    # 2. Get active attempt detail (verifies deterministic question list)
    resp = await async_client.get(
        f"/api/v1/quizzes/{quiz_id}/attempts/{attempt_id}",
        headers=data["student1_headers"],
    )
    assert resp.status_code == 200
    assert resp.json()["attempt_id"] == attempt_id

    # 3. Submit correct answers
    resp = await async_client.post(
        f"/api/v1/quizzes/{quiz_id}/attempts/{attempt_id}/submit",
        json={
            "answers": [
                {
                    "question_id": question_id,
                    "selected_answer_ids": [correct_ans_id],
                }
            ]
        },
        headers=data["student1_headers"],
    )
    assert resp.status_code == 200
    result = resp.json()
    assert result["score"] == 100.0
    assert result["passed"] is True
    assert result["status"] == "SUBMITTED"

    # 4. Resubmitting already finalized attempt is rejected (400)
    resp = await async_client.post(
        f"/api/v1/quizzes/{quiz_id}/attempts/{attempt_id}/submit",
        json={"answers": []},
        headers=data["student1_headers"],
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_course_completion_and_certification(async_client, setup_phase6_data):
    data = setup_phase6_data
    course_id = data["course1_id"]
    lesson_id = data["lesson1_id"]
    quiz_id = data["quiz1_id"]
    question_id = data["question1_id"]
    correct_ans_id = data["correct_ans1_id"]

    # 1. Check completion before completing requirements
    resp = await async_client.get(
        f"/api/v1/courses/{course_id}/completion",
        headers=data["student1_headers"],
    )
    assert resp.status_code == 200
    comp = resp.json()
    assert comp["is_completed"] is False
    assert comp["eligible_for_certificate"] is False

    # 2. Attempting to get certificate before completion is rejected (400)
    resp = await async_client.get(
        f"/api/v1/courses/{course_id}/certificate",
        headers=data["student1_headers"],
    )
    assert resp.status_code == 400

    # 3. Complete lesson 1
    resp = await async_client.post(
        f"/api/v1/lessons/{lesson_id}/progress",
        json={"is_completed": True, "progress_percentage": 100.0},
        headers=data["student1_headers"],
    )
    assert resp.status_code == 200

    # 4. Pass quiz 1
    resp = await async_client.post(
        f"/api/v1/quizzes/{quiz_id}/attempts",
        json={
            "submissions": [
                {
                    "question_id": question_id,
                    "selected_answer_ids": [correct_ans_id],
                }
            ]
        },
        headers=data["student1_headers"],
    )
    assert resp.status_code == 201
    assert resp.json()["passed"] is True

    # 5. Verify course completion reaches 100%
    resp = await async_client.get(
        f"/api/v1/courses/{course_id}/completion",
        headers=data["student1_headers"],
    )
    assert resp.status_code == 200
    comp = resp.json()
    assert comp["is_completed"] is True
    assert comp["completion_percentage"] == 100.0
    assert comp["eligible_for_certificate"] is True

    # 6. Issue Certificate
    resp = await async_client.get(
        f"/api/v1/courses/{course_id}/certificate",
        headers=data["student1_headers"],
    )
    assert resp.status_code == 200
    cert = resp.json()
    assert cert["certificate_number"].startswith("CERT-2026-")
    assert cert["student_name"] == data["student1_name"]
    assert cert["course_title"] == data["course1_title"]
    assert cert["verification_hash"] is not None

    # 7. Duplicate certificate generation is idempotent (returns same certificate)
    resp2 = await async_client.get(
        f"/api/v1/courses/{course_id}/certificate",
        headers=data["student1_headers"],
    )
    assert resp2.status_code == 200
    assert resp2.json()["id"] == cert["id"]
    assert resp2.json()["certificate_number"] == cert["certificate_number"]

    # 8. Public verification endpoint validates certificate
    resp_v = await async_client.get(f"/api/v1/certificates/verify/{cert['certificate_number']}")
    assert resp_v.status_code == 200
    v_data = resp_v.json()
    assert v_data["is_valid"] is True
    assert v_data["student_name"] == data["student1_name"]
    assert v_data["course_title"] == data["course1_title"]
