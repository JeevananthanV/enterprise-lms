from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.module import CourseModule
from app.models.lesson import Lesson
from app.repositories.course_repository import course_repository, generate_slug
from app.repositories.module_repository import module_repository
from app.repositories.lesson_repository import lesson_repository
from app.schemas.module import ModuleCreate, ModuleUpdate
from app.schemas.lesson import LessonCreate, LessonUpdate
from app.core.dependencies import require_resource_owner_or_admin
from app.services.cache_service import cache_service


class CurriculumService:
    async def create_module(
        self,
        db: AsyncSession,
        course_id: str,
        module_in: ModuleCreate,
        current_user: User,
    ) -> CourseModule:
        course = await course_repository.get(db, course_id)
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")
        require_resource_owner_or_admin(course.instructor_id, current_user)

        order_index = module_in.order_index
        if not order_index:
            order_index = await module_repository.get_next_order_index(db, course_id)

        module = CourseModule(
            course_id=course_id,
            title=module_in.title.strip(),
            description=module_in.description.strip() if module_in.description else None,
            order_index=order_index,
            is_published=module_in.is_published,
        )
        created = await module_repository.create(db, module)
        await cache_service.invalidate_course_cache(course_id)
        return created

    async def list_modules(
        self,
        db: AsyncSession,
        course_id: str,
        current_user: User,
    ) -> List[CourseModule]:
        course = await course_repository.get(db, course_id)
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")
        require_resource_owner_or_admin(course.instructor_id, current_user)
        return await module_repository.get_by_course(db, course_id)

    async def get_module(
        self,
        db: AsyncSession,
        module_id: str,
        current_user: User,
    ) -> CourseModule:
        module = await module_repository.get(db, module_id)
        if not module:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found.")
        course = await course_repository.get(db, module.course_id)
        if course:
            require_resource_owner_or_admin(course.instructor_id, current_user)
        return module

    async def update_module(
        self,
        db: AsyncSession,
        module_id: str,
        module_in: ModuleUpdate,
        current_user: User,
    ) -> CourseModule:
        module = await self.get_module(db, module_id, current_user)
        update_dict = module_in.model_dump(exclude_unset=True)

        if "title" in update_dict and update_dict["title"]:
            module.title = update_dict["title"].strip()
        if "description" in update_dict:
            module.description = update_dict["description"]
        if "order_index" in update_dict and update_dict["order_index"] is not None:
            module.order_index = update_dict["order_index"]
        if "is_published" in update_dict and update_dict["is_published"] is not None:
            module.is_published = update_dict["is_published"]

        await db.commit()
        await db.refresh(module)
        await cache_service.invalidate_course_cache(module.course_id)
        return module

    async def delete_module(
        self,
        db: AsyncSession,
        module_id: str,
        current_user: User,
    ) -> None:
        module = await self.get_module(db, module_id, current_user)
        course_id = module.course_id
        await module_repository.delete(db, module_id)
        await cache_service.invalidate_course_cache(course_id)

    async def reorder_modules(
        self,
        db: AsyncSession,
        course_id: str,
        ordered_ids: List[str],
        current_user: User,
    ) -> List[CourseModule]:
        course = await course_repository.get(db, course_id)
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")
        require_resource_owner_or_admin(course.instructor_id, current_user)

        try:
            reordered = await module_repository.reorder_modules(db, course_id, ordered_ids)
            await cache_service.invalidate_course_cache(course_id)
            return reordered
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # --- Lesson Operations ---

    async def create_lesson(
        self,
        db: AsyncSession,
        module_id: str,
        lesson_in: LessonCreate,
        current_user: User,
    ) -> Lesson:
        module = await self.get_module(db, module_id, current_user)

        order_index = lesson_in.order_index
        if not order_index:
            order_index = await lesson_repository.get_next_order_index(db, module_id)

        slug = lesson_in.slug or generate_slug(lesson_in.title)

        lesson = Lesson(
            module_id=module_id,
            title=lesson_in.title.strip(),
            slug=slug,
            content_type=lesson_in.content_type,
            content=lesson_in.content,
            duration_minutes=lesson_in.duration_minutes,
            order_index=order_index,
            is_published=lesson_in.is_published,
            is_free_preview=lesson_in.is_free_preview,
        )
        created = await lesson_repository.create(db, lesson)
        await cache_service.invalidate_course_cache(module.course_id)
        return created

    async def list_lessons(
        self,
        db: AsyncSession,
        module_id: str,
        current_user: User,
    ) -> List[Lesson]:
        await self.get_module(db, module_id, current_user)
        return await lesson_repository.get_by_module(db, module_id)

    async def get_lesson(
        self,
        db: AsyncSession,
        lesson_id: str,
        current_user: User,
    ) -> Lesson:
        lesson = await lesson_repository.get(db, lesson_id)
        if not lesson:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found.")
        await self.get_module(db, lesson.module_id, current_user)
        return lesson

    async def update_lesson(
        self,
        db: AsyncSession,
        lesson_id: str,
        lesson_in: LessonUpdate,
        current_user: User,
    ) -> Lesson:
        lesson = await self.get_lesson(db, lesson_id, current_user)
        module = await module_repository.get(db, lesson.module_id)
        course_id = module.course_id if module else None

        update_dict = lesson_in.model_dump(exclude_unset=True)

        if "title" in update_dict and update_dict["title"]:
            lesson.title = update_dict["title"].strip()
        if "slug" in update_dict and update_dict["slug"]:
            lesson.slug = update_dict["slug"].strip().lower()
        if "content_type" in update_dict and update_dict["content_type"]:
            lesson.content_type = update_dict["content_type"]
        if "content" in update_dict:
            lesson.content = update_dict["content"]
        if "duration_minutes" in update_dict and update_dict["duration_minutes"] is not None:
            lesson.duration_minutes = update_dict["duration_minutes"]
        if "order_index" in update_dict and update_dict["order_index"] is not None:
            lesson.order_index = update_dict["order_index"]
        if "is_published" in update_dict and update_dict["is_published"] is not None:
            lesson.is_published = update_dict["is_published"]
        if "is_free_preview" in update_dict and update_dict["is_free_preview"] is not None:
            lesson.is_free_preview = update_dict["is_free_preview"]

        await db.commit()
        await db.refresh(lesson)
        if course_id:
            await cache_service.invalidate_course_cache(course_id)
        return lesson

    async def delete_lesson(
        self,
        db: AsyncSession,
        lesson_id: str,
        current_user: User,
    ) -> None:
        lesson = await self.get_lesson(db, lesson_id, current_user)
        module = await module_repository.get(db, lesson.module_id)
        course_id = module.course_id if module else None
        await lesson_repository.delete(db, lesson_id)
        if course_id:
            await cache_service.invalidate_course_cache(course_id)

    async def reorder_lessons(
        self,
        db: AsyncSession,
        module_id: str,
        ordered_ids: List[str],
        current_user: User,
    ) -> List[Lesson]:
        module = await self.get_module(db, module_id, current_user)
        try:
            reordered = await lesson_repository.reorder_lessons(db, module_id, ordered_ids)
            if module and module.course_id:
                await cache_service.invalidate_course_cache(module.course_id)
            return reordered
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


curriculum_service = CurriculumService()

