from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User, UserRole
from app.core.dependencies import get_current_user, require_any_role
from app.services.assignment_service import assignment_service
from app.schemas.assessment import (
    AssignmentCreate,
    AssignmentResponse,
    AssignmentSubmissionResponse,
    SubmissionGradeRequest,
)

router = APIRouter(prefix="/instructor", tags=["Instructor Assessments & Grading"])


@router.post("/courses/{course_id}/assignments", response_model=AssignmentResponse)
async def create_course_assignment(
    course_id: str,
    data: AssignmentCreate,
    current_user: User = Depends(require_any_role([UserRole.INSTRUCTOR, UserRole.PLATFORM_ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """Create a new course assignment for an instructor's course."""
    if data.course_id != course_id:
        data.course_id = course_id
    return await assignment_service.create_assignment(db, current_user, data)


@router.get("/courses/{course_id}/assignments", response_model=List[AssignmentResponse])
async def list_course_assignments_instructor(
    course_id: str,
    current_user: User = Depends(require_any_role([UserRole.INSTRUCTOR, UserRole.PLATFORM_ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """List assignments for an instructor course."""
    return await assignment_service.list_course_assignments(db, current_user, course_id)


@router.get("/assignments/{id}/submissions", response_model=List[AssignmentSubmissionResponse])
async def list_assignment_submissions(
    id: str,
    current_user: User = Depends(require_any_role([UserRole.INSTRUCTOR, UserRole.PLATFORM_ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """List all student submissions for an assignment with strict course ownership isolation."""
    return await assignment_service.list_assignment_submissions_for_instructor(db, current_user, id)


@router.get("/submissions/{id}", response_model=AssignmentSubmissionResponse)
async def get_submission_details(
    id: str,
    current_user: User = Depends(require_any_role([UserRole.INSTRUCTOR, UserRole.PLATFORM_ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """View single student submission details with course ownership check."""
    return await assignment_service.get_submission_for_instructor(db, current_user, id)


@router.post("/submissions/{id}/grade", response_model=AssignmentSubmissionResponse)
async def grade_submission(
    id: str,
    data: SubmissionGradeRequest,
    current_user: User = Depends(require_any_role([UserRole.INSTRUCTOR, UserRole.PLATFORM_ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """Grade student submission with score and feedback (enforcing course ownership)."""
    return await assignment_service.grade_submission(db, current_user, id, data)
