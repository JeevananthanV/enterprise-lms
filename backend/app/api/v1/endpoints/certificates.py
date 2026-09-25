from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User, UserRole
from app.core.dependencies import get_current_user, require_any_role
from app.services.certificate_service import certificate_service
from app.services.course_completion_service import course_completion_service
from app.schemas.assessment import (
    CertificateResponse,
    CertificateVerifyResponse,
    CourseCompletionReport,
)

router = APIRouter(tags=["Certificates & Completion"])


@router.get("/courses/{course_id}/completion", response_model=CourseCompletionReport)
async def get_course_completion_report(
    course_id: str,
    current_user: User = Depends(require_any_role([UserRole.STUDENT, UserRole.PLATFORM_ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """Calculates real-time completion report across lessons, quizzes, and assignments."""
    return await course_completion_service.calculate_course_completion(
        db, current_user.id, course_id
    )


@router.get("/courses/{course_id}/certificate", response_model=CertificateResponse)
async def get_or_issue_course_certificate(
    course_id: str,
    current_user: User = Depends(require_any_role([UserRole.STUDENT, UserRole.PLATFORM_ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """Issues or fetches the official verified completion certificate upon 100% course completion."""
    return await certificate_service.get_or_issue_certificate(
        db, current_user, course_id
    )


@router.get("/certificates/{certificate_id}", response_model=CertificateResponse)
async def get_certificate_by_id(
    certificate_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch certificate by ID."""
    return await certificate_service.get_certificate_by_id(db, certificate_id)


@router.get("/certificates/verify/{certificate_number}", response_model=CertificateVerifyResponse)
async def verify_certificate_public(
    certificate_number: str,
    db: AsyncSession = Depends(get_db),
):
    """Public verification endpoint to validate certificate authenticity."""
    return await certificate_service.verify_certificate(db, certificate_number)
