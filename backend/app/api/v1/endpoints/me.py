from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.user import User, UserRole
from app.core.dependencies import get_current_user, require_any_role
from app.schemas.learning import (
    EnrollmentWithCourseResponse,
    StudentOverallProgressResponse,
)
from app.services.enrollment_service import enrollment_service
from app.services.progress_service import progress_service

router = APIRouter()


@router.get("/enrollments", response_model=List[EnrollmentWithCourseResponse])
async def get_my_enrollments(
    current_user: User = Depends(require_any_role([UserRole.STUDENT, UserRole.PLATFORM_ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all active and completed course enrollments for the authenticated student.
    Includes course metadata, progress percentage, and last accessed lesson.
    """
    return await enrollment_service.get_student_enrollments(db, user_id=current_user.id)


@router.get("/progress", response_model=StudentOverallProgressResponse)
async def get_my_progress(
    current_user: User = Depends(require_any_role([UserRole.STUDENT, UserRole.PLATFORM_ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """
    Get comprehensive learning progress statistics across all courses for the authenticated student.
    """
    return await progress_service.get_student_overall_progress(db, user_id=current_user.id)
