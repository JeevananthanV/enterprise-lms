from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.models.lesson import Lesson
from app.repositories.lesson_repository import lesson_repository
from app.repositories.content_repository import content_repository
from app.repositories.enrollment_repository import enrollment_repository
from app.schemas.content import (
    LessonContentCreateRequest,
    LessonContentUpdateRequest,
    LessonContentResponse,
    ContentTypeEnum,
)
from app.core.logging import logger


from app.services.cache_service import cache_service


class ContentService:
    """Service orchestrating MongoDB Lesson Content and PostgreSQL metadata."""

    async def _get_lesson_and_verify_access(
        self,
        db: AsyncSession,
        lesson_id: str,
        user: User,
        require_write: bool = False,
    ) -> Lesson:
        lesson = await lesson_repository.get_with_course(db, lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lesson '{lesson_id}' not found",
            )

        course = lesson.module.course if lesson.module else None
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent course not found for lesson",
            )

        # Platform Admin has global write/read access
        if user.role == UserRole.PLATFORM_ADMIN:
            return lesson

        # Instructor must own the course
        if user.role == UserRole.INSTRUCTOR:
            if course.instructor_id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Forbidden: You can only manage content for courses you own",
                )
            return lesson

        # If write access is required and user is neither Admin nor Instructor
        if require_write:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: Only course instructors and administrators can manage lesson content",
            )

        # Read access for Student:
        # Check if lesson is free preview or student is enrolled
        if lesson.is_free_preview:
            return lesson

        enrollment = await enrollment_repository.get_by_user_and_course(
            db, user_id=user.id, course_id=course.id
        )
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: You must be enrolled in this course to view lesson content",
            )

        return lesson

    async def create_lesson_content(
        self,
        db: AsyncSession,
        lesson_id: str,
        payload: LessonContentCreateRequest,
        user: User,
    ) -> LessonContentResponse:
        lesson = await self._get_lesson_and_verify_access(db, lesson_id, user, require_write=True)

        # Check if content already exists
        existing = await content_repository.get_by_lesson_id(db, lesson_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Content for lesson '{lesson_id}' already exists. Use PUT to update.",
            )

        course_id = lesson.module.course_id if lesson.module else None

        doc_data = {
            "lesson_id": lesson_id,
            "course_id": course_id,
            "content_type": payload.content_type.value,
            "body": payload.body,
            "video_metadata": payload.video_metadata.model_dump() if payload.video_metadata else None,
            "pdf_metadata": payload.pdf_metadata.model_dump() if payload.pdf_metadata else None,
            "transcript": payload.transcript.model_dump() if payload.transcript else None,
            "external_resources": [r.model_dump() for r in (payload.external_resources or [])],
            "custom_properties": payload.custom_properties or {},
            "is_published": False,
            "published_at": None,
        }

        created_doc = await content_repository.create_content(db, doc_data)

        # Link content_ref in PostgreSQL
        await lesson_repository.update_content_ref(db, lesson_id, created_doc["id"])
        if course_id:
            await cache_service.invalidate_course_cache(course_id)

        logger.info(f"Created lesson content '{created_doc['id']}' for lesson '{lesson_id}'")
        return LessonContentResponse(**created_doc)

    async def get_lesson_content(
        self,
        db: AsyncSession,
        lesson_id: str,
        user: User,
    ) -> LessonContentResponse:
        lesson = await self._get_lesson_and_verify_access(db, lesson_id, user, require_write=False)

        content_doc = await content_repository.get_by_lesson_id(db, lesson_id)
        if not content_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Content for lesson '{lesson_id}' has not been created yet",
            )

        # If user is a student, ensure content is published
        if user.role == UserRole.STUDENT and not content_doc.get("is_published", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Lesson content has not been published yet",
            )

        return LessonContentResponse(**content_doc)

    async def update_lesson_content(
        self,
        db: AsyncSession,
        lesson_id: str,
        payload: LessonContentUpdateRequest,
        user: User,
    ) -> LessonContentResponse:
        lesson = await self._get_lesson_and_verify_access(db, lesson_id, user, require_write=True)
        course_id = lesson.module.course_id if lesson.module else None

        existing = await content_repository.get_by_lesson_id(db, lesson_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Content for lesson '{lesson_id}' not found. Create it first using POST.",
            )

        update_dict: Dict[str, Any] = {}
        if payload.content_type is not None:
            update_dict["content_type"] = payload.content_type.value
        if payload.body is not None:
            update_dict["body"] = payload.body
        if payload.video_metadata is not None:
            update_dict["video_metadata"] = payload.video_metadata.model_dump()
        if payload.pdf_metadata is not None:
            update_dict["pdf_metadata"] = payload.pdf_metadata.model_dump()
        if payload.transcript is not None:
            update_dict["transcript"] = payload.transcript.model_dump()
        if payload.external_resources is not None:
            update_dict["external_resources"] = [r.model_dump() for r in payload.external_resources]
        if payload.custom_properties is not None:
            update_dict["custom_properties"] = payload.custom_properties

        updated_doc = await content_repository.update_content(db, lesson_id, update_dict)
        if not updated_doc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update lesson content document",
            )

        if course_id:
            await cache_service.invalidate_course_cache(course_id)

        logger.info(f"Updated lesson content for lesson '{lesson_id}', version incremented to {updated_doc.get('version')}")
        return LessonContentResponse(**updated_doc)

    async def publish_lesson_content(
        self,
        db: AsyncSession,
        lesson_id: str,
        user: User,
    ) -> LessonContentResponse:
        lesson = await self._get_lesson_and_verify_access(db, lesson_id, user, require_write=True)
        course_id = lesson.module.course_id if lesson.module else None

        existing = await content_repository.get_by_lesson_id(db, lesson_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Content for lesson '{lesson_id}' not found",
            )

        updated_doc = await content_repository.set_published_status(db, lesson_id, is_published=True)
        if not updated_doc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to publish lesson content document",
            )

        if course_id:
            await cache_service.invalidate_course_cache(course_id)

        logger.info(f"Published lesson content for lesson '{lesson_id}'")
        return LessonContentResponse(**updated_doc)

    async def unpublish_lesson_content(
        self,
        db: AsyncSession,
        lesson_id: str,
        user: User,
    ) -> LessonContentResponse:
        lesson = await self._get_lesson_and_verify_access(db, lesson_id, user, require_write=True)
        course_id = lesson.module.course_id if lesson.module else None

        existing = await content_repository.get_by_lesson_id(db, lesson_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Content for lesson '{lesson_id}' not found",
            )

        updated_doc = await content_repository.set_published_status(db, lesson_id, is_published=False)
        if not updated_doc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to unpublish lesson content document",
            )

        if course_id:
            await cache_service.invalidate_course_cache(course_id)

        logger.info(f"Unpublished lesson content for lesson '{lesson_id}'")
        return LessonContentResponse(**updated_doc)


content_service = ContentService()

