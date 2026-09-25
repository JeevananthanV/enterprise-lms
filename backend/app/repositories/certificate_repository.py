from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.certificate import Certificate
from app.repositories.base import BaseRepository


class CertificateRepository(BaseRepository[Certificate]):
    def __init__(self):
        super().__init__(Certificate)

    async def get_by_id_with_relations(self, db: AsyncSession, certificate_id: str) -> Optional[Certificate]:
        stmt = (
            select(Certificate)
            .where(Certificate.id == certificate_id)
            .options(
                selectinload(Certificate.student),
                selectinload(Certificate.course),
                selectinload(Certificate.enrollment),
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_enrollment_id(self, db: AsyncSession, enrollment_id: str) -> Optional[Certificate]:
        stmt = (
            select(Certificate)
            .where(Certificate.enrollment_id == enrollment_id)
            .options(
                selectinload(Certificate.student),
                selectinload(Certificate.course),
                selectinload(Certificate.enrollment),
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_number(self, db: AsyncSession, certificate_number: str) -> Optional[Certificate]:
        stmt = (
            select(Certificate)
            .where(Certificate.certificate_number == certificate_number)
            .options(
                selectinload(Certificate.student),
                selectinload(Certificate.course),
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_student(self, db: AsyncSession, student_id: int) -> List[Certificate]:
        stmt = (
            select(Certificate)
            .where(Certificate.student_id == student_id)
            .options(
                selectinload(Certificate.course),
                selectinload(Certificate.student),
            )
            .order_by(Certificate.issued_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_student_and_course(
        self, db: AsyncSession, student_id: int, course_id: str
    ) -> Optional[Certificate]:
        stmt = (
            select(Certificate)
            .where(
                Certificate.student_id == student_id,
                Certificate.course_id == course_id,
            )
            .options(
                selectinload(Certificate.student),
                selectinload(Certificate.course),
                selectinload(Certificate.enrollment),
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


certificate_repository = CertificateRepository()
