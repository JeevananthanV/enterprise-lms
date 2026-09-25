from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.user import User, UserRole
from app.core.dependencies import get_current_user, require_any_role
from app.schemas.learning import LessonProgressUpdateRequest, LessonProgressResponse
from app.services.progress_service import progress_service

router = APIRouter()


@router.get("/status")
async def lessons_domain_status():
    return {"domain": "lessons", "status": "registered", "phase": "Phase 2+"}


@router.post("/{lesson_id}/progress", response_model=LessonProgressResponse)
async def update_lesson_progress(
    lesson_id: str,
    payload: LessonProgressUpdateRequest,
    current_user: User = Depends(require_any_role([UserRole.STUDENT, UserRole.PLATFORM_ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """
    Idempotently record or toggle lesson completion progress for an authenticated student.
    Automatically triggers course completion calculation.
    """
    return await progress_service.record_lesson_progress(
        db,
        user=current_user,
        lesson_id=lesson_id,
        is_completed=payload.is_completed,
    )
