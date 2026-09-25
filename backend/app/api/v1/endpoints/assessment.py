from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.user import User, UserRole
from app.core.dependencies import get_current_user, require_any_role
from app.schemas.learning import (
    QuizPublicResponse,
    QuizAttemptSubmitRequest,
    QuizAttemptResponse,
    QuizResultDetailResponse,
)
from app.services.quiz_service import quiz_service

router = APIRouter()


@router.get("/status")
async def assessment_domain_status():
    return {"domain": "assessment", "status": "registered", "phase": "Phase 2+"}


@router.get("/{quiz_id}", response_model=QuizPublicResponse)
async def get_quiz(
    quiz_id: str,
    current_user: User = Depends(require_any_role([UserRole.STUDENT, UserRole.INSTRUCTOR, UserRole.PLATFORM_ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """
    Get sanitized quiz questions and answer choices for the student.
    Correct answers are withheld to ensure integrity.
    """
    return await quiz_service.get_sanitized_quiz_for_student(
        db, user=current_user, quiz_id=quiz_id
    )


@router.post("/{quiz_id}/attempts", response_model=QuizAttemptResponse, status_code=status.HTTP_201_CREATED)
async def submit_quiz_attempt(
    quiz_id: str,
    payload: QuizAttemptSubmitRequest,
    current_user: User = Depends(require_any_role([UserRole.STUDENT, UserRole.PLATFORM_ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit a quiz attempt (single-step mode).
    Score is calculated authoritative server-side against stored answer keys.
    """
    return await quiz_service.submit_quiz_attempt(
        db,
        user=current_user,
        quiz_id=quiz_id,
        submissions=payload.submissions,
    )


@router.post("/{quiz_id}/attempts/start", status_code=status.HTTP_201_CREATED)
async def start_timed_quiz_attempt(
    quiz_id: str,
    current_user: User = Depends(require_any_role([UserRole.STUDENT, UserRole.PLATFORM_ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """
    Starts a timed quiz attempt, sets server-side expires_at, and locks question sequence/randomization.
    """
    return await quiz_service.start_timed_attempt(db, user=current_user, quiz_id=quiz_id)


@router.get("/{quiz_id}/attempts/{attempt_id}")
async def get_timed_quiz_attempt(
    quiz_id: str,
    attempt_id: str,
    current_user: User = Depends(require_any_role([UserRole.STUDENT, UserRole.PLATFORM_ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """
    Get active attempt detail with remaining time and question list.
    """
    return await quiz_service.get_attempt_detail(db, user=current_user, attempt_id=attempt_id)


@router.post("/{quiz_id}/attempts/{attempt_id}/submit")
async def submit_timed_quiz_attempt(
    quiz_id: str,
    attempt_id: str,
    payload: dict,
    current_user: User = Depends(require_any_role([UserRole.STUDENT, UserRole.PLATFORM_ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit answers for a timed quiz attempt with server-authoritative timer validation.
    """
    from app.schemas.assessment import TimedQuizSubmitRequest
    req = TimedQuizSubmitRequest.model_validate(payload)
    return await quiz_service.submit_timed_attempt(
        db, user=current_user, quiz_id=quiz_id, attempt_id=attempt_id, data=req
    )


@router.get("/{quiz_id}/results", response_model=QuizResultDetailResponse)
async def get_quiz_results(
    quiz_id: str,
    current_user: User = Depends(require_any_role([UserRole.STUDENT, UserRole.PLATFORM_ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """
    Get past quiz attempts, score history, and passing status for the authenticated student.
    """
    return await quiz_service.get_student_quiz_results(
        db, user=current_user, quiz_id=quiz_id
    )
