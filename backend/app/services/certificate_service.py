import uuid
import hashlib
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.user import User
from app.models.course import Course
from app.models.certificate import Certificate
from app.repositories.certificate_repository import certificate_repository
from app.repositories.enrollment_repository import enrollment_repository
from app.repositories.course_repository import course_repository
from app.services.course_completion_service import course_completion_service
from app.schemas.assessment import CertificateResponse, CertificateVerifyResponse


class CertificateService:
    def _generate_verification_hash(self, student_id: int, course_id: str, cert_number: str) -> str:
        """Create a cryptographic SHA-256 fingerprint for the certificate."""
        raw = f"ENTERPRISE-LMS:{student_id}:{course_id}:{cert_number}:AUTH-KEY-2026"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _generate_certificate_number(self) -> str:
        """Create a human-readable unique serial: CERT-2026-XXXXX."""
        unique_suffix = uuid.uuid4().hex[:8].upper()
        return f"CERT-2026-{unique_suffix}"

    async def get_or_issue_certificate(
        self,
        db: AsyncSession,
        current_user: User,
        course_id: str,
    ) -> CertificateResponse:
        """
        Issues or returns an existing certificate for an enrolled student who has 100% completed the course.
        """
        enrollment = await enrollment_repository.get_by_user_and_course(
            db, current_user.id, course_id
        )
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="You are not enrolled in this course.",
            )

        existing = await certificate_repository.get_by_enrollment_id(db, enrollment.id)
        if existing:
            return self._build_certificate_response(existing)

        # Check course completion authoritatively
        report = await course_completion_service.calculate_course_completion(
            db, current_user.id, course_id
        )
        if not report.is_completed or report.completion_percentage < 100.0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Course is not fully completed ({report.completion_percentage}%). All lessons, quizzes, and assignments must be completed.",
            )

        course = await course_repository.get_by_id(db, course_id)
        cert_number = self._generate_certificate_number()
        v_hash = self._generate_verification_hash(current_user.id, course_id, cert_number)
        now = datetime.now(timezone.utc)

        cert = Certificate(
            id=str(uuid.uuid4()),
            certificate_number=cert_number,
            enrollment_id=enrollment.id,
            student_id=current_user.id,
            course_id=course_id,
            issued_at=now,
            completion_date=enrollment.completed_at or now,
            verification_hash=v_hash,
            pdf_url=f"/api/v1/certificates/{cert_number}/download",
        )

        db.add(cert)
        await db.commit()
        await db.refresh(cert)

        loaded_cert = await certificate_repository.get_by_id_with_relations(db, cert.id)
        return self._build_certificate_response(loaded_cert or cert)

    async def get_certificate_by_id(
        self,
        db: AsyncSession,
        certificate_id: str,
    ) -> CertificateResponse:
        """Fetch certificate by ID with relations."""
        cert = await certificate_repository.get_by_id_with_relations(db, certificate_id)
        if not cert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Certificate not found.",
            )
        return self._build_certificate_response(cert)

    async def get_student_course_certificate(
        self,
        db: AsyncSession,
        student_id: int,
        course_id: str,
    ) -> CertificateResponse:
        """Fetch a specific student's certificate for a course."""
        cert = await certificate_repository.get_by_student_and_course(db, student_id, course_id)
        if not cert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Certificate not found for this course.",
            )
        return self._build_certificate_response(cert)

    async def verify_certificate(
        self,
        db: AsyncSession,
        certificate_number: str,
    ) -> CertificateVerifyResponse:
        """Public certificate verification endpoint."""
        cert = await certificate_repository.get_by_number(db, certificate_number)
        if not cert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Certificate not found or invalid.",
            )

        return CertificateVerifyResponse(
            is_valid=True,
            certificate_number=cert.certificate_number,
            student_name=cert.student.full_name if cert.student else "Student",
            course_title=cert.course.title if cert.course else "Course",
            issued_at=cert.issued_at,
            completion_date=cert.completion_date,
            verification_hash=cert.verification_hash,
            verification_url=f"/verify/certificate/{cert.certificate_number}",
        )

    def _build_certificate_response(self, cert: Certificate) -> CertificateResponse:
        return CertificateResponse(
            id=cert.id,
            certificate_number=cert.certificate_number,
            enrollment_id=cert.enrollment_id,
            student_id=cert.student_id,
            course_id=cert.course_id,
            issued_at=cert.issued_at,
            completion_date=cert.completion_date,
            verification_hash=cert.verification_hash,
            pdf_url=cert.pdf_url,
            course_title=cert.course.title if cert.course else "",
            student_name=cert.student.full_name if cert.student else "",
            instructor_name=cert.course.instructor.full_name if (cert.course and cert.course.instructor) else "",
        )


certificate_service = CertificateService()
