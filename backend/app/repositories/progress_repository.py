from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.progress import LessonProgress
from app.models.lesson import Lesson
from app.models.module import CourseModule


class ProgressRepository:

    async def get_by_user_and_lesson(
        self,
        db: AsyncSession,
        user_id: int,
        lesson_id: str,
    ) -> Optional[LessonProgress]:
        """Fetch lesson progress for specific student and lesson."""
        result = await db.execute(
            select(LessonProgress).where(
                LessonProgress.user_id == user_id,
                LessonProgress.lesson_id == lesson_id,
            )
        )
        return result.scalars().first()

    async def upsert_lesson_progress(
        self,
        db: AsyncSession,
        user_id: int,
        lesson_id: str,
        is_completed: bool,
    ) -> LessonProgress:
        """Idempotently insert or update lesson progress."""
        progress = await self.get_by_user_and_lesson(
            db,
            user_id,
            lesson_id,
        )

        now = datetime.now(timezone.utc)

        if not progress:
            progress = LessonProgress(
                user_id=user_id,
                lesson_id=lesson_id,
                is_completed=is_completed,
                completed_at=now if is_completed else None,
                last_accessed_at=now,
            )
            db.add(progress)
        else:
            progress.last_accessed_at = now

            if is_completed:
                progress.is_completed = True

                if not progress.completed_at:
                    progress.completed_at = now
            else:
                progress.is_completed = False
                progress.completed_at = None

        await db.commit()
        await db.refresh(progress)

        return progress

    async def get_completed_lesson_ids_for_course(
        self,
        db: AsyncSession,
        user_id: int,
        course_id: str,
    ) -> List[str]:
        """Get all completed lesson IDs for a specific student and course."""
        query = (
            select(LessonProgress.lesson_id)
            .join(
                Lesson,
                Lesson.id == LessonProgress.lesson_id,
            )
            .join(
                CourseModule,
                CourseModule.id == Lesson.module_id,
            )
            .where(
                LessonProgress.user_id == user_id,
                CourseModule.course_id == course_id,
                LessonProgress.is_completed == True,
            )
        )

        result = await db.execute(query)

        return list(result.scalars().all())

    async def get_completed_lesson_ids_by_course(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> dict[str, set[str]]:
        """Aggregate all completed lesson IDs by course for a user in one query."""
        query = (
            select(CourseModule.course_id, LessonProgress.lesson_id)
            .join(
                Lesson,
                Lesson.id == LessonProgress.lesson_id,
            )
            .join(
                CourseModule,
                CourseModule.id == Lesson.module_id,
            )
            .where(
                LessonProgress.user_id == user_id,
                LessonProgress.is_completed == True,
            )
        )

        result = await db.execute(query)
        by_course: dict[str, set[str]] = {}
        for course_id, lesson_id in result.all():
            by_course.setdefault(course_id, set()).add(lesson_id)
        return by_course

    async def get_all_progress_for_user(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> List[LessonProgress]:
        """
        Get all lesson progress records for a student.

        Lesson and module are eagerly loaded to avoid
        additional database queries when accessing:
        progress.lesson
        progress.lesson.module
        """
        result = await db.execute(
            select(LessonProgress)
            .options(
                selectinload(LessonProgress.lesson)
                .selectinload(Lesson.module)
            )
            .where(
                LessonProgress.user_id == user_id
            )
        )

        return list(result.scalars().all())


progress_repository = ProgressRepository()