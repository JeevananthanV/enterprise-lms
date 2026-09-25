import pytest
import pytest_asyncio
import uuid
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.base import Base
from app.models.user import User, UserRole
from app.models.role import Role, user_roles
from app.models.course import Course, CourseStatus, CourseLevel
from app.models.module import CourseModule
from app.models.lesson import Lesson, LessonContentType
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.progress import LessonProgress
from app.models.quiz import Quiz, Question, Answer, QuizAttempt, QuestionType
from app.models.notification import Notification, NotificationType
from app.models.audit import AuditLog
from app.db.seed import seed_all, seed_roles, seed_demo_users


@pytest.mark.asyncio
async def test_user_role_relationships(db_session):
    """Test Many-to-Many User <-> Role relationship."""
    # Create role
    role_admin = Role(name=f"TEST_ADMIN_{uuid.uuid4().hex[:6]}", description="Test Administrator Role")
    db_session.add(role_admin)
    await db_session.flush()

    # Create user and associate role
    user = User(
        email=f"test.user.{uuid.uuid4().hex[:6]}@example.com",
        hashed_password="hashedpassword123",
        full_name="Test User",
        role=UserRole.PLATFORM_ADMIN,
    )
    user.roles.append(role_admin)
    db_session.add(user)
    await db_session.commit()

    # Query back and verify relationship
    res = await db_session.execute(select(User).where(User.id == user.id))
    fetched_user = res.scalars().first()
    assert fetched_user is not None
    assert len(fetched_user.roles) == 1
    assert fetched_user.roles[0].name == role_admin.name


@pytest.mark.asyncio
async def test_course_ownership_and_cascades(db_session):
    """Test Course ownership by instructor and module cascading on delete."""
    # Create instructor
    instructor = User(
        email=f"instructor.{uuid.uuid4().hex[:6]}@example.com",
        hashed_password="hashedpassword123",
        full_name="Instructor Alice",
        role=UserRole.INSTRUCTOR,
    )
    db_session.add(instructor)
    await db_session.flush()

    # Create course
    course_slug = f"course-{uuid.uuid4().hex[:6]}"
    course = Course(
        title="Enterprise Software Architecture",
        slug=course_slug,
        description="Comprehensive architecture course",
        status=CourseStatus.PUBLISHED,
        level=CourseLevel.ADVANCED,
        price=149.00,
        instructor_id=instructor.id,
    )
    db_session.add(course)
    await db_session.flush()

    # Verify course ownership relationship
    assert course.instructor_id == instructor.id
    assert course.instructor.full_name == "Instructor Alice"

    # Add module to course
    module = CourseModule(
        course_id=course.id,
        title="Module 1: Domain-Driven Design",
        order_index=1,
    )
    db_session.add(module)
    await db_session.commit()

    # Verify module link
    res = await db_session.execute(select(Course).where(Course.id == course.id))
    fetched_course = res.scalars().first()
    assert len(fetched_course.modules) == 1
    assert fetched_course.modules[0].title == "Module 1: Domain-Driven Design"


@pytest.mark.asyncio
async def test_enrollment_uniqueness_constraint(db_session):
    """Test that a user cannot enroll in the same course more than once (UniqueConstraint)."""
    student = User(
        email=f"student.{uuid.uuid4().hex[:6]}@example.com",
        hashed_password="hashedpassword123",
        full_name="Student Bob",
        role=UserRole.STUDENT,
    )
    instructor = User(
        email=f"instructor.{uuid.uuid4().hex[:6]}@example.com",
        hashed_password="hashedpassword123",
        full_name="Instructor Charlie",
        role=UserRole.INSTRUCTOR,
    )
    db_session.add_all([student, instructor])
    await db_session.flush()

    course = Course(
        title="Python Mastery",
        slug=f"python-mastery-{uuid.uuid4().hex[:6]}",
        instructor_id=instructor.id,
    )
    db_session.add(course)
    await db_session.flush()

    # First enrollment
    enrollment1 = Enrollment(
        user_id=student.id,
        course_id=course.id,
        status=EnrollmentStatus.ACTIVE,
    )
    db_session.add(enrollment1)
    await db_session.commit()

    # Duplicate enrollment should trigger IntegrityError
    enrollment2 = Enrollment(
        user_id=student.id,
        course_id=course.id,
        status=EnrollmentStatus.ACTIVE,
    )
    db_session.add(enrollment2)
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()


@pytest.mark.asyncio
async def test_module_and_lesson_ordering_and_uniqueness(db_session):
    """Test module/lesson order uniqueness and ordering constraints."""
    instructor = User(
        email=f"instructor.{uuid.uuid4().hex[:6]}@example.com",
        hashed_password="hashedpassword123",
        full_name="Instructor David",
        role=UserRole.INSTRUCTOR,
    )
    db_session.add(instructor)
    await db_session.flush()

    course = Course(
        title="Microservices Design",
        slug=f"microservices-{uuid.uuid4().hex[:6]}",
        instructor_id=instructor.id,
    )
    db_session.add(course)
    await db_session.flush()

    # Add module with order_index 1
    module1 = CourseModule(course_id=course.id, title="Module 1", order_index=1)
    db_session.add(module1)
    await db_session.commit()
    module1_id = module1.id

    # Attempt to add duplicate order_index 1 in same course should fail
    duplicate_module = CourseModule(course_id=course.id, title="Module 1 Duplicate", order_index=1)
    db_session.add(duplicate_module)
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()

    # Add lessons with order index
    lesson1 = Lesson(
        module_id=module1_id,
        title="Lesson 1",
        slug=f"lesson-1-{uuid.uuid4().hex[:6]}",
        order_index=1,
    )
    db_session.add(lesson1)
    await db_session.commit()

    duplicate_lesson = Lesson(
        module_id=module1_id,
        title="Lesson 1 Duplicate",
        slug=f"lesson-1-dup-{uuid.uuid4().hex[:6]}",
        order_index=1,
    )
    db_session.add(duplicate_lesson)
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()


@pytest.mark.asyncio
async def test_quiz_questions_answers_and_progress(db_session):
    """Test Quiz, Question, Answer, LessonProgress, and QuizAttempt relationships."""
    instructor = User(
        email=f"instructor.{uuid.uuid4().hex[:6]}@example.com",
        hashed_password="hashedpassword123",
        full_name="Instructor Elena",
        role=UserRole.INSTRUCTOR,
    )
    student = User(
        email=f"student.{uuid.uuid4().hex[:6]}@example.com",
        hashed_password="hashedpassword123",
        full_name="Student Frank",
        role=UserRole.STUDENT,
    )
    db_session.add_all([instructor, student])
    await db_session.flush()

    course = Course(
        title="DevOps Essentials",
        slug=f"devops-{uuid.uuid4().hex[:6]}",
        instructor_id=instructor.id,
    )
    db_session.add(course)
    await db_session.flush()

    module = CourseModule(course_id=course.id, title="CI/CD Pipelines", order_index=1)
    db_session.add(module)
    await db_session.flush()

    lesson = Lesson(
        module_id=module.id,
        title="GitHub Actions CI",
        slug=f"gha-ci-{uuid.uuid4().hex[:6]}",
        order_index=1,
    )
    db_session.add(lesson)
    await db_session.flush()

    # Quiz linked to course and lesson
    quiz = Quiz(
        course_id=course.id,
        lesson_id=lesson.id,
        title="CI/CD Evaluation",
        passing_score=80,
    )
    db_session.add(quiz)
    await db_session.flush()

    # Question and answers
    question = Question(
        quiz_id=quiz.id,
        question_text="What is a runner in GitHub Actions?",
        question_type=QuestionType.SINGLE_CHOICE,
        points=2,
        order_index=1,
    )
    db_session.add(question)
    await db_session.flush()

    answer1 = Answer(
        question_id=question.id,
        answer_text="An application that runs a job from a GitHub Actions workflow",
        is_correct=True,
        order_index=1,
    )
    answer2 = Answer(
        question_id=question.id,
        answer_text="A Git branch merging algorithm",
        is_correct=False,
        order_index=2,
    )
    db_session.add_all([answer1, answer2])
    await db_session.flush()

    # Student Lesson Progress
    progress = LessonProgress(
        user_id=student.id,
        lesson_id=lesson.id,
        is_completed=True,
    )
    db_session.add(progress)

    # Student Quiz Attempt
    attempt = QuizAttempt(
        user_id=student.id,
        quiz_id=quiz.id,
        score=100.0,
        passed=True,
        attempt_number=1,
    )
    db_session.add(attempt)
    await db_session.commit()

    # Verify relationships query
    res = await db_session.execute(select(Quiz).where(Quiz.id == quiz.id))
    fetched_quiz = res.scalars().first()
    assert fetched_quiz is not None
    assert len(fetched_quiz.questions) == 1
    assert len(fetched_quiz.questions[0].answers) == 2
    assert fetched_quiz.questions[0].answers[0].is_correct is True
    assert len(fetched_quiz.attempts) == 1
    assert fetched_quiz.attempts[0].passed is True


@pytest.mark.asyncio
async def test_notifications_and_audit_logs(db_session):
    """Test Notifications and AuditLog persistence and user linking."""
    user = User(
        email=f"user.{uuid.uuid4().hex[:6]}@example.com",
        hashed_password="hashedpassword123",
        full_name="Grace Hopper",
        role=UserRole.STUDENT,
    )
    db_session.add(user)
    await db_session.flush()

    notification = Notification(
        user_id=user.id,
        title="Welcome to the Platform",
        message="Your account has been activated.",
        notification_type=NotificationType.SYSTEM,
    )
    db_session.add(notification)

    audit = AuditLog(
        user_id=user.id,
        action="USER_LOGIN",
        resource_type="User",
        resource_id=str(user.id),
        ip_address="127.0.0.1",
        user_agent="pytest-client",
    )
    db_session.add(audit)
    await db_session.commit()

    # Verify
    res = await db_session.execute(select(User).where(User.id == user.id))
    fetched_user = res.scalars().first()
    assert len(fetched_user.notifications) == 1
    assert fetched_user.notifications[0].title == "Welcome to the Platform"
    assert len(fetched_user.audit_logs) == 1
    assert fetched_user.audit_logs[0].action == "USER_LOGIN"


@pytest.mark.asyncio
async def test_seed_data_completeness(db_session):
    """Test that seed_all creates 1 Admin, 2 Instructors, 5 Students, 3 Courses, modules, lessons, and quizzes."""
    await seed_all(db_session)

    # Verify users count and roles
    res_users = await db_session.execute(select(User))
    all_users = res_users.scalars().all()

    admins = [u for u in all_users if u.role == UserRole.PLATFORM_ADMIN]
    instructors = [u for u in all_users if u.role == UserRole.INSTRUCTOR]
    students = [u for u in all_users if u.role == UserRole.STUDENT]

    assert len(admins) >= 1
    assert len(instructors) >= 2
    assert len(students) >= 5

    # Verify courses
    res_courses = await db_session.execute(select(Course))
    courses = res_courses.scalars().all()
    assert len(courses) >= 3

    # Verify modules, lessons, quizzes
    res_modules = await db_session.execute(select(CourseModule))
    modules = res_modules.scalars().all()
    assert len(modules) >= 6

    res_lessons = await db_session.execute(select(Lesson))
    lessons = res_lessons.scalars().all()
    assert len(lessons) >= 10

    res_quizzes = await db_session.execute(select(Quiz))
    quizzes = res_quizzes.scalars().all()
    assert len(quizzes) >= 3

    res_questions = await db_session.execute(select(Question))
    questions = res_questions.scalars().all()
    assert len(questions) >= 4

    res_answers = await db_session.execute(select(Answer))
    answers = res_answers.scalars().all()
    assert len(answers) >= 10
