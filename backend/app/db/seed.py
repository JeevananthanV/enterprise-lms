import os
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.base import Base
from app.models.role import Role, user_roles
from app.models.user import User, UserRole
from app.models.course import Course, CourseStatus, CourseLevel
from app.models.module import CourseModule
from app.models.lesson import Lesson, LessonContentType
from app.models.quiz import Quiz, Question, Answer, QuestionType
from app.core.security import hash_password
from app.core.config import settings
from app.core.logging import logger


async def seed_roles(db: AsyncSession) -> Dict[str, Role]:
    """Seed standard RBAC roles into the roles table."""
    roles_data = [
        {"name": "PLATFORM_ADMIN", "description": "Platform Administrator with full system control"},
        {"name": "INSTRUCTOR", "description": "Instructor with course authoring and grading capabilities"},
        {"name": "STUDENT", "description": "Student with course enrollment and learning access"},
    ]
    created_roles = {}
    for r_data in roles_data:
        res = await db.execute(select(Role).where(Role.name == r_data["name"]))
        role = res.scalars().first()
        if not role:
            role = Role(name=r_data["name"], description=r_data["description"])
            db.add(role)
            await db.flush()
            logger.info(f"Seeded role: {role.name}")
        created_roles[role.name] = role
    await db.commit()
    return created_roles


async def seed_demo_users(db: AsyncSession) -> Dict[str, User]:
    """
    Seed initial 1 Admin, 2 Instructors, and 5 Students.
    Credentials are read from environment variables with secure local-development fallbacks.
    Never seeds credentials in production.
    """
    if not settings.SEED_DEMO_USERS or settings.ENVIRONMENT == "production":
        logger.info("Demo user seeding skipped (disabled or production environment).")
        return {}

    roles_map = await seed_roles(db)

    # Password configuration via environment
    admin_pw = settings.SEED_ADMIN_PASSWORD or os.getenv("SEED_ADMIN_PASSWORD", "AdminPass123!")
    instructor_pw = settings.SEED_INSTRUCTOR_PASSWORD or os.getenv("SEED_INSTRUCTOR_PASSWORD", "InstructorPass123!")
    student_pw = settings.SEED_STUDENT_PASSWORD or os.getenv("SEED_STUDENT_PASSWORD", "StudentPass123!")

    users_data: List[Dict[str, Any]] = [
        # 1 Platform Admin
        {
            "email": settings.SEED_ADMIN_EMAIL or "admin@lms.enterprise.local",
            "password": admin_pw,
            "full_name": "Platform Administrator",
            "role": UserRole.PLATFORM_ADMIN,
        },
        # 2 Instructors
        {
            "email": settings.SEED_INSTRUCTOR_EMAIL or "instructor@lms.enterprise.local",
            "password": instructor_pw,
            "full_name": "Dr. Sarah Vance",
            "role": UserRole.INSTRUCTOR,
        },
        {
            "email": "marcus.sterling@lms.enterprise.local",
            "password": instructor_pw,
            "full_name": "Prof. Marcus Sterling",
            "role": UserRole.INSTRUCTOR,
        },
        # 5 Students
        {
            "email": settings.SEED_STUDENT_EMAIL or "student@lms.enterprise.local",
            "password": student_pw,
            "full_name": "Alex Chen",
            "role": UserRole.STUDENT,
        },
        {
            "email": "maya.lin@lms.enterprise.local",
            "password": student_pw,
            "full_name": "Maya Lin",
            "role": UserRole.STUDENT,
        },
        {
            "email": "carlos.rodriguez@lms.enterprise.local",
            "password": student_pw,
            "full_name": "Carlos Rodriguez",
            "role": UserRole.STUDENT,
        },
        {
            "email": "aisha.patel@lms.enterprise.local",
            "password": student_pw,
            "full_name": "Aisha Patel",
            "role": UserRole.STUDENT,
        },
        {
            "email": "liam.oconnor@lms.enterprise.local",
            "password": student_pw,
            "full_name": "Liam O'Connor",
            "role": UserRole.STUDENT,
        },
    ]

    seeded_users: Dict[str, User] = {}
    for u_data in users_data:
        email = u_data["email"].lower().strip()
        res = await db.execute(select(User).where(User.email == email))
        user = res.scalars().first()
        if not user:
            user = User(
                email=email,
                hashed_password=hash_password(u_data["password"]),
                full_name=u_data["full_name"],
                role=u_data["role"],
                is_active=True,
            )
            # Associate RBAC role
            role_obj = roles_map.get(u_data["role"].value)
            if role_obj:
                user.roles.append(role_obj)
            db.add(user)
            await db.flush()
            logger.info(f"Seeded user: {email} [{u_data['role'].value}]")
        seeded_users[email] = user

    await db.commit()
    return seeded_users


async def seed_courses_and_curriculum(db: AsyncSession, users_map: Dict[str, User]) -> None:
    """
    Seed/synchronize 3 complete enterprise courses with structured modules,
    lessons, flexible content fallbacks, and assessment quizzes.
    """
    if not settings.SEED_DEMO_USERS or settings.ENVIRONMENT == "production":
        return

    from app.db.sync_courses import sync_all_courses
    await sync_all_courses(db)



async def seed_all(db: AsyncSession) -> None:
    """Master seed function executed during startup or seeding CLI."""
    users_map = await seed_demo_users(db)
    if users_map:
        await seed_courses_and_curriculum(db, users_map)
