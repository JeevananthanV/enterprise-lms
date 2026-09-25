from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User, UserRole
from app.core.dependencies import get_current_user, require_any_role
from app.services.assignment_service import assignment_service
from app.services.storage_service import storage_service
from app.schemas.assessment import (
    AssignmentResponse,
    AssignmentSubmissionCreate,
    AssignmentSubmissionResponse,
)

router = APIRouter(prefix="/assignments", tags=["Assignments"])


@router.get("/{id}", response_model=AssignmentResponse)
async def get_assignment(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """View assignment details (requires enrollment for students)."""
    return await assignment_service.get_assignment(db, current_user, id)


@router.get("/course/{course_id}", response_model=List[AssignmentResponse])
async def list_course_assignments(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all assignments for a course."""
    return await assignment_service.list_course_assignments(db, current_user, course_id)


@router.post("/{id}/submissions", response_model=AssignmentSubmissionResponse)
async def submit_assignment_json(
    id: str,
    data: AssignmentSubmissionCreate,
    current_user: User = Depends(require_any_role([UserRole.STUDENT, UserRole.PLATFORM_ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """Submit text or previously uploaded file reference for an assignment."""
    return await assignment_service.submit_assignment(db, current_user, id, data)


@router.post("/{id}/submissions/upload", response_model=AssignmentSubmissionResponse)
async def submit_assignment_with_file(
    id: str,
    submission_text: Optional[str] = Form(default=None),
    file: UploadFile = File(...),
    current_user: User = Depends(require_any_role([UserRole.STUDENT, UserRole.PLATFORM_ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """Upload a file and create/update submission in one atomic operation."""
    assignment = await assignment_service.get_assignment(db, current_user, id)
    file_url, original_name, size = await storage_service.save_upload(
        file,
        allowed_types_str=assignment.allowed_file_types,
        max_size_mb=assignment.max_file_size_mb,
    )

    data = AssignmentSubmissionCreate(
        submission_text=submission_text,
        file_url=file_url,
        file_name=original_name,
        file_size_bytes=size,
    )
    return await assignment_service.submit_assignment(db, current_user, id, data)


@router.get("/{id}/submissions/me", response_model=Optional[AssignmentSubmissionResponse])
async def get_my_submission(
    id: str,
    current_user: User = Depends(require_any_role([UserRole.STUDENT, UserRole.PLATFORM_ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """Get the authenticated student's submission status, score, and instructor feedback."""
    return await assignment_service.get_student_submission(db, current_user, id)


@router.get("/submissions/files/{filename}")
async def download_submission_file(
    filename: str,
    current_user: User = Depends(get_current_user),
):
    """Safely stream / download an uploaded assignment submission file."""
    file_path = storage_service.get_file_path(filename)
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream",
    )
