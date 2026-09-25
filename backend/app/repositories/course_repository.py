import re
import uuid
from typing import Optional, List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, desc
from sqlalchemy.orm import selectinload

from app.repositories.base import BaseRepository
from app.models.course import Course, CourseStatus, CourseLevel
from app.models.module import CourseModule
from app.models.lesson import Lesson


def generate_slug(text: str) -> str:
    """Generate a clean URL slug from title string."""
    s = text.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_-]+", "-", s)
    s = re.sub(r"^-+|-+$", "", s)
    return s or str(uuid.uuid4())[:8]


class CourseRepository(BaseRepository[Course]):

    def __init__(self):
        super().__init__(Course)

    async def get(
        self,
        db: AsyncSession,
        id: str
    ) -> Optional[Course]:
        """
        Get a course with its modules, lessons,
        and associated quizzes eagerly loaded.
        """
        result = await db.execute(
            select(Course)
            .options(
                selectinload(Course.modules)
                .selectinload(CourseModule.lessons)
                .selectinload(Lesson.quiz)
            )
            .where(Course.id == id)
        )

        return result.scalars().first()

    async def get_by_slug(
        self,
        db: AsyncSession,
        slug: str
    ) -> Optional[Course]:
        """Get a course by its slug."""
        result = await db.execute(
            select(Course).where(
                Course.slug == slug.lower().strip()
            )
        )

        return result.scalars().first()

    async def ensure_unique_slug(
        self,
        db: AsyncSession,
        base_title: str,
        current_course_id: Optional[str] = None
    ) -> str:
        """Generate a unique course slug."""
        base_slug = generate_slug(base_title)
        candidate = base_slug
        counter = 1

        while True:
            query = select(Course).where(
                Course.slug == candidate
            )

            if current_course_id:
                query = query.where(
                    Course.id != current_course_id
                )

            result = await db.execute(query)
            existing = result.scalars().first()

            if not existing:
                return candidate

            candidate = f"{base_slug}-{counter}"
            counter += 1

    async def list_by_instructor(
        self,
        db: AsyncSession,
        instructor_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Course]:
        """List courses belonging to an instructor."""

        query = select(Course)

        if instructor_id is not None:
            query = query.where(
                Course.instructor_id == instructor_id
            )

        query = (
            query
            .order_by(desc(Course.updated_at))
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(query)

        return list(result.scalars().all())

    async def list_published(
        self,
        db: AsyncSession,
        *,
        search: Optional[str] = None,
        category: Optional[str] = None,
        level: Optional[CourseLevel] = None,
        skip: int = 0,
        limit: int = 12,
    ) -> Tuple[List[Course], int]:
        """
        List published courses with pagination and filters.

        Uses direct count and filtered course queries
        to avoid the overhead of counting a subquery.
        """

        filters = [
            Course.status == CourseStatus.PUBLISHED
        ]

        # Search filter
        if search and search.strip():
            search_pattern = f"%{search.strip().lower()}%"

            filters.append(
                or_(
                    func.lower(Course.title).like(search_pattern),
                    func.lower(Course.short_description).like(search_pattern),
                    func.lower(Course.description).like(search_pattern),
                )
            )

        # Category filter
        if (
            category
            and category.strip()
            and category.lower() != "all"
        ):
            filters.append(
                func.lower(Course.category)
                == category.strip().lower()
            )

        # Level filter
        if level:
            filters.append(
                Course.level == level
            )

        # Count matching courses
        count_query = (
            select(func.count(Course.id))
            .where(*filters)
        )

        count_result = await db.execute(count_query)
        total = count_result.scalar_one()

        # Fetch current page
        items_query = (
            select(Course)
            .where(*filters)
            .order_by(desc(Course.created_at))
            .offset(skip)
            .limit(limit)
        )

        items_result = await db.execute(items_query)
        items = list(items_result.scalars().all())

        return items, total

    async def get_counts(
        self,
        db: AsyncSession,
        course_id: str
    ) -> Tuple[int, int]:
        """Return (module_count, lesson_count) for a course."""

        mod_count = (
            await db.execute(
                select(func.count(CourseModule.id))
                .where(
                    CourseModule.course_id == course_id
                )
            )
        ).scalar_one()

        lesson_count = (
            await db.execute(
                select(func.count(Lesson.id))
                .join(
                    CourseModule,
                    Lesson.module_id == CourseModule.id
                )
                .where(
                    CourseModule.course_id == course_id
                )
            )
        ).scalar_one()

        return mod_count, lesson_count


course_repository = CourseRepository()