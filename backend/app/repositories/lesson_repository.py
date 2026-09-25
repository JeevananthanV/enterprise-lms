from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.repositories.base import BaseRepository
from app.models.lesson import Lesson
from app.models.module import CourseModule
from sqlalchemy.orm import selectinload


class LessonRepository(BaseRepository[Lesson]):
    def __init__(self):
        super().__init__(Lesson)

    async def get_with_course(self, db: AsyncSession, lesson_id: str) -> Optional[Lesson]:
        result = await db.execute(
            select(Lesson)
            .where(Lesson.id == lesson_id)
            .options(
                selectinload(Lesson.module).selectinload(CourseModule.course)
            )
        )
        return result.scalars().first()

    async def update_content_ref(self, db: AsyncSession, lesson_id: str, content_ref: Optional[str]) -> Optional[Lesson]:
        lesson = await self.get_by_id(db, lesson_id)
        if lesson:
            lesson.content_ref = content_ref
            await db.commit()
            await db.refresh(lesson)
        return lesson

    async def get_by_module(self, db: AsyncSession, module_id: str) -> List[Lesson]:
        result = await db.execute(
            select(Lesson)
            .where(Lesson.module_id == module_id)
            .order_by(Lesson.order_index)
        )
        return list(result.scalars().all())

    async def get_next_order_index(self, db: AsyncSession, module_id: str) -> int:
        result = await db.execute(
            select(func.coalesce(func.max(Lesson.order_index), 0)).where(
                Lesson.module_id == module_id
            )
        )
        return (result.scalar_one() or 0) + 1

    async def reorder_lessons(self, db: AsyncSession, module_id: str, ordered_ids: List[str]) -> List[Lesson]:
        """
        Reorder lessons in a module collision-free using a temporary offset to satisfy the unique constraint.
        """
        lessons = await self.get_by_module(db, module_id)
        lesson_map = {l.id: l for l in lessons}

        for lid in ordered_ids:
            if lid not in lesson_map:
                raise ValueError(f"Lesson {lid} does not belong to module {module_id}")

        # Step 1: Shift to negative offset to avoid unique constraint collisions
        for idx, lid in enumerate(ordered_ids, start=1):
            les = lesson_map[lid]
            les.order_index = -(idx + 1000)
        await db.flush()

        # Step 2: Assign final sequential positive order indices
        for idx, lid in enumerate(ordered_ids, start=1):
            les = lesson_map[lid]
            les.order_index = idx

        await db.commit()
        return await self.get_by_module(db, module_id)


lesson_repository = LessonRepository()

