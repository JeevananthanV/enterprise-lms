from fastapi import APIRouter
from app.api.v1.endpoints import (
    health,
    auth,
    users,
    me,
    instructor,
    courses,
    modules,
    lessons,
    enrollment,
    progress,
    assessment,
    assignments,
    instructor_assessment,
    certificates,
    analytics,
    notifications,
    audit,
    content,
)

api_router = APIRouter()

# Health & Diagnostics
api_router.include_router(health.router, tags=["Health"])

# Domain Modular Boundaries & Learning APIs
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(me.router, prefix="/me", tags=["Student Profile & Learning"])
api_router.include_router(instructor.router, prefix="/instructor", tags=["Instructor Studio"])
api_router.include_router(instructor_assessment.router, tags=["Instructor Assessments & Grading"])
api_router.include_router(courses.router, prefix="/courses", tags=["Courses"])
api_router.include_router(modules.router, prefix="/modules", tags=["Modules"])
api_router.include_router(lessons.router, prefix="/lessons", tags=["Lessons"])
api_router.include_router(content.router, prefix="/lessons", tags=["Lesson Flexible Content"])
api_router.include_router(enrollment.router, prefix="/enrollment", tags=["Enrollment"])
api_router.include_router(progress.router, prefix="/progress", tags=["Progress"])
api_router.include_router(assessment.router, prefix="/assessment", tags=["Assessment"])
api_router.include_router(assessment.router, prefix="/quizzes", tags=["Quizzes"])
api_router.include_router(assignments.router, tags=["Assignments"])
api_router.include_router(certificates.router, tags=["Certificates & Completion"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(audit.router, prefix="/audit", tags=["Audit"])

