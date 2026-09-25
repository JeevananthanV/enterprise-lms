from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.assignment import Assignment, AssignmentSubmission, SubmissionStatus
from app.repositories.base import BaseRepository


class AssignmentRepository(BaseRepository[Assignment]):
    def __init__(self):
        super().__init__(Assignment)

    async def get_by_id_with_relations(self, db: AsyncSession, assignment_id: str) -> Optional[Assignment]:
        stmt = (
            select(Assignment)
            .where(Assignment.id == assignment_id)
            .options(
                selectinload(Assignment.course),
                selectinload(Assignment.submissions),
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_course(self, db: AsyncSession, course_id: str) -> List[Assignment]:
        stmt = (
            select(Assignment)
            .where(Assignment.course_id == course_id)
            .options(selectinload(Assignment.submissions))
            .order_by(Assignment.created_at.asc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    # --- Submission Methods ---

    async def get_submission(self, db: AsyncSession, assignment_id: str, student_id: int) -> Optional[AssignmentSubmission]:
        stmt = (
            select(AssignmentSubmission)
            .where(
                AssignmentSubmission.assignment_id == assignment_id,
                AssignmentSubmission.student_id == student_id,
            )
            .options(
                selectinload(AssignmentSubmission.assignment),
                selectinload(AssignmentSubmission.student),
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_submission_by_id(self, db: AsyncSession, submission_id: str) -> Optional[AssignmentSubmission]:
        stmt = (
            select(AssignmentSubmission)
            .where(AssignmentSubmission.id == submission_id)
            .options(
                selectinload(AssignmentSubmission.assignment).selectinload(Assignment.course),
                selectinload(AssignmentSubmission.student),
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_submissions_for_assignment(self, db: AsyncSession, assignment_id: str) -> List[AssignmentSubmission]:
        stmt = (
            select(AssignmentSubmission)
            .where(AssignmentSubmission.assignment_id == assignment_id)
            .options(
                selectinload(AssignmentSubmission.student),
                selectinload(AssignmentSubmission.assignment),
            )
            .order_by(AssignmentSubmission.submitted_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def list_submissions_for_course(self, db: AsyncSession, course_id: str) -> List[AssignmentSubmission]:
        stmt = (
            select(AssignmentSubmission)
            .join(Assignment, Assignment.id == AssignmentSubmission.assignment_id)
            .where(Assignment.course_id == course_id)
            .options(
                selectinload(AssignmentSubmission.student),
                selectinload(AssignmentSubmission.assignment),
            )
            .order_by(AssignmentSubmission.submitted_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def create_submission(self, db: AsyncSession, submission: AssignmentSubmission) -> AssignmentSubmission:
        db.add(submission)
        await db.commit()
        await db.refresh(submission)
        return submission

    async def update_submission(self, db: AsyncSession, submission: AssignmentSubmission) -> AssignmentSubmission:
        await db.commit()
        await db.refresh(submission)
        return submission


assignment_repository = AssignmentRepository()
