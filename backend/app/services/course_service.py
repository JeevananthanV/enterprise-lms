from typing import Optional, List, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.models.course import Course, CourseStatus
from app.repositories.course_repository import course_repository
from app.schemas.course import (
    CourseCreate,
    CourseUpdate,
    CoursePublishChecklist,
    CourseResponse,
)
from app.core.dependencies import require_resource_owner_or_admin


from app.services.cache_service import cache_service


class CourseService:
    async def create_course(
        self,
        db: AsyncSession,
        course_in: CourseCreate,
        current_user: User,
    ) -> Course:
        slug = course_in.slug
        if not slug:
            slug = await course_repository.ensure_unique_slug(db, course_in.title)
        else:
            existing = await course_repository.get_by_slug(db, slug)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Course with slug '{slug}' already exists.",
                )

        course = Course(
            title=course_in.title.strip(),
            slug=slug,
            short_description=course_in.short_description.strip() if course_in.short_description else None,
            description=course_in.description.strip() if course_in.description else None,
            category=course_in.category.strip() if course_in.category else "General",
            level=course_in.level,
            price=course_in.price,
            thumbnail_url=course_in.thumbnail_url,
            estimated_duration_minutes=course_in.estimated_duration_minutes,
            status=CourseStatus.DRAFT,
            instructor_id=current_user.id,
        )
        created = await course_repository.create(db, course)
        await cache_service.delete_pattern("courses:catalog:*")
        await cache_service.delete_pattern("analytics:summary:*")
        return created

    async def get_instructor_courses(
        self,
        db: AsyncSession,
        current_user: User,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Course]:
        # Admins can view all courses, Instructors view own
        instructor_id = None if current_user.role == UserRole.PLATFORM_ADMIN else current_user.id
        return await course_repository.list_by_instructor(db, instructor_id=instructor_id, skip=skip, limit=limit)

    async def get_course_by_id(
        self,
        db: AsyncSession,
        course_id: str,
        current_user: Optional[User] = None,
        enforce_published: bool = False,
    ) -> Course:
        course = await course_repository.get(db, course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found.",
            )

        if enforce_published and course.status != CourseStatus.PUBLISHED:
            # Only allow owner or admin to view unpublished course details
            if not current_user or (current_user.id != course.instructor_id and current_user.role != UserRole.PLATFORM_ADMIN):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Course is not published.",
                )

        return course

    async def update_course(
        self,
        db: AsyncSession,
        course_id: str,
        course_in: CourseUpdate,
        current_user: User,
    ) -> Course:
        course = await self.get_course_by_id(db, course_id, current_user)
        require_resource_owner_or_admin(course.instructor_id, current_user)

        update_dict = course_in.model_dump(exclude_unset=True)

        if "title" in update_dict and update_dict["title"]:
            course.title = update_dict["title"].strip()
            if "slug" not in update_dict:
                course.slug = await course_repository.ensure_unique_slug(db, course.title, current_course_id=course.id)

        if "slug" in update_dict and update_dict["slug"]:
            slug_cand = update_dict["slug"].strip().lower()
            existing = await course_repository.get_by_slug(db, slug_cand)
            if existing and existing.id != course.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Slug '{slug_cand}' is already in use by another course.",
                )
            course.slug = slug_cand

        if "short_description" in update_dict:
            course.short_description = update_dict["short_description"]
        if "description" in update_dict:
            course.description = update_dict["description"]
        if "category" in update_dict and update_dict["category"]:
            course.category = update_dict["category"].strip()
        if "level" in update_dict and update_dict["level"]:
            course.level = update_dict["level"]
        if "price" in update_dict and update_dict["price"] is not None:
            course.price = update_dict["price"]
        if "thumbnail_url" in update_dict:
            course.thumbnail_url = update_dict["thumbnail_url"]
        if "estimated_duration_minutes" in update_dict and update_dict["estimated_duration_minutes"] is not None:
            course.estimated_duration_minutes = update_dict["estimated_duration_minutes"]
        if "status" in update_dict and update_dict["status"]:
            course.status = update_dict["status"]

        await db.commit()
        await db.refresh(course)
        await cache_service.invalidate_course_cache(course.id)
        return course

    async def delete_course(
        self,
        db: AsyncSession,
        course_id: str,
        current_user: User,
    ) -> None:
        course = await self.get_course_by_id(db, course_id, current_user)
        require_resource_owner_or_admin(course.instructor_id, current_user)
        await course_repository.delete(db, course_id)
        await cache_service.invalidate_course_cache(course_id)

    async def get_publish_checklist(
        self,
        db: AsyncSession,
        course: Course,
    ) -> CoursePublishChecklist:
        errors = []
        has_valid_title = bool(course.title and len(course.title.strip()) >= 3)
        if not has_valid_title:
            errors.append("Course title must be at least 3 characters long.")

        has_description = bool(course.description and len(course.description.strip()) >= 10)
        if not has_description:
            errors.append("Course description must be at least 10 characters long.")

        mod_count, lesson_count = await course_repository.get_counts(db, course.id)
        if mod_count == 0:
            errors.append("Course must have at least one module.")
        if lesson_count == 0:
            errors.append("Course must have at least one lesson across its modules.")

        is_publishable = len(errors) == 0

        return CoursePublishChecklist(
            is_publishable=is_publishable,
            has_valid_title=has_valid_title,
            has_description=has_description,
            module_count=mod_count,
            lesson_count=lesson_count,
            errors=errors,
        )

    async def publish_course(
        self,
        db: AsyncSession,
        course_id: str,
        current_user: User,
    ) -> Course:
        course = await self.get_course_by_id(db, course_id, current_user)
        require_resource_owner_or_admin(course.instructor_id, current_user)

        checklist = await self.get_publish_checklist(db, course)
        if not checklist.is_publishable:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Course does not satisfy publishing prerequisites.",
                    "errors": checklist.errors,
                    "checklist": checklist.model_dump(),
                },
            )

        course.status = CourseStatus.PUBLISHED
        await db.commit()
        await db.refresh(course)
        await cache_service.invalidate_course_cache(course_id)
        return course

    async def unpublish_course(
        self,
        db: AsyncSession,
        course_id: str,
        current_user: User,
    ) -> Course:
        course = await self.get_course_by_id(db, course_id, current_user)
        require_resource_owner_or_admin(course.instructor_id, current_user)

        course.status = CourseStatus.UNPUBLISHED
        await db.commit()
        await db.refresh(course)
        await cache_service.invalidate_course_cache(course_id)
        return course


course_service = CourseService()

