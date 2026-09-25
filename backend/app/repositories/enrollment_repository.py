from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from app.repositories.base import BaseRepository
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.course import Course


class EnrollmentRepository(BaseRepository[Enrollment]):
    def __init__(self):
        super().__init__(Enrollment)

    async def get_by_user_and_course(
        self, db: AsyncSession, user_id: int, course_id: str
    ) -> Optional[Enrollment]:
        """Fetch enrollment by composite key."""
        result = await db.execute(
            select(Enrollment).where(
                Enrollment.user_id == user_id,
                Enrollment.course_id == course_id,
            )
        )
        return result.scalars().first()

    async def list_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        status: Optional[EnrollmentStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Enrollment]:
        """Fetch all enrollments for a user, ordered by enrollment date."""
        query = (
            select(Enrollment)
            .options(selectinload(Enrollment.course).selectinload(Course.instructor))
            .where(Enrollment.user_id == user_id)
        )
        if status:
            query = query.where(Enrollment.status == status)
        query = query.order_by(desc(Enrollment.enrolled_at)).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def count_by_user(
        self, db: AsyncSession, user_id: int, status: Optional[EnrollmentStatus] = None
    ) -> int:
        """Count enrollments for user."""
        query = select(func.count(Enrollment.id)).where(Enrollment.user_id == user_id)
        if status:
            query = query.where(Enrollment.status == status)
        result = await db.execute(query)
        return result.scalar() or 0


enrollment_repository = EnrollmentRepository()
