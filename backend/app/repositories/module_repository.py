from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from app.repositories.base import BaseRepository
from app.models.module import CourseModule


class ModuleRepository(BaseRepository[CourseModule]):
    def __init__(self):
        super().__init__(CourseModule)

    async def get_by_course(self, db: AsyncSession, course_id: str) -> List[CourseModule]:
        result = await db.execute(
            select(CourseModule)
            .where(CourseModule.course_id == course_id)
            .order_by(CourseModule.order_index)
        )
        return list(result.scalars().all())

    async def get_next_order_index(self, db: AsyncSession, course_id: str) -> int:
        result = await db.execute(
            select(func.coalesce(func.max(CourseModule.order_index), 0)).where(
                CourseModule.course_id == course_id
            )
        )
        return (result.scalar_one() or 0) + 1

    async def reorder_modules(self, db: AsyncSession, course_id: str, ordered_ids: List[str]) -> List[CourseModule]:
        """
        Reorder modules in a course collision-free using a temporary offset to satisfy the unique constraint.
        """
        modules = await self.get_by_course(db, course_id)
        mod_map = {m.id: m for m in modules}

        # Validate that all IDs belong to this course
        for mid in ordered_ids:
            if mid not in mod_map:
                raise ValueError(f"Module {mid} does not belong to course {course_id}")

        # Step 1: Shift order_index to temporary negative indices to avoid uniqueness collisions
        for idx, mid in enumerate(ordered_ids, start=1):
            mod = mod_map[mid]
            mod.order_index = -(idx + 1000)
        await db.flush()

        # Step 2: Set final positive sequential order_index (1-indexed)
        for idx, mid in enumerate(ordered_ids, start=1):
            mod = mod_map[mid]
            mod.order_index = idx

        await db.commit()
        return await self.get_by_course(db, course_id)


module_repository = ModuleRepository()
