from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User, UserRole
from app.core.dependencies import get_current_user, require_authenticated_user, require_any_role
from app.schemas.content import (
    LessonContentCreateRequest,
    LessonContentUpdateRequest,
    LessonContentResponse,
)
from app.services.content_service import content_service

router = APIRouter()


@router.post(
    "/{lesson_id}/content",
    response_model=LessonContentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create flexible lesson content in MongoDB",
)
async def create_lesson_content(
    lesson_id: str,
    payload: LessonContentCreateRequest,
    current_user: User = Depends(require_any_role([UserRole.INSTRUCTOR, UserRole.PLATFORM_ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """
    Create flexible MongoDB content document for a lesson.
    Only course instructors (for their own courses) and platform admins can create content.
    """
    return await content_service.create_lesson_content(
        db=db,
        lesson_id=lesson_id,
        payload=payload,
        user=current_user,
    )


@router.get(
    "/{lesson_id}/content",
    response_model=LessonContentResponse,
    summary="Get lesson content from MongoDB",
)
async def get_lesson_content(
    lesson_id: str,
    current_user: User = Depends(require_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve flexible MongoDB content for a lesson.
    Students can access published content for enrolled courses or free-preview lessons.
    Instructors can access content for courses they own.
    Platform admins have global access.
    """
    return await content_service.get_lesson_content(
        db=db,
        lesson_id=lesson_id,
        user=current_user,
    )


@router.put(
    "/{lesson_id}/content",
    response_model=LessonContentResponse,
    summary="Update lesson content in MongoDB",
)
async def update_lesson_content(
    lesson_id: str,
    payload: LessonContentUpdateRequest,
    current_user: User = Depends(require_any_role([UserRole.INSTRUCTOR, UserRole.PLATFORM_ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """
    Update MongoDB content document for a lesson.
    Automatically increments document version and records updated_at timestamp.
    Only course instructors and platform admins can update content.
    """
    return await content_service.update_lesson_content(
        db=db,
        lesson_id=lesson_id,
        payload=payload,
        user=current_user,
    )


@router.post(
    "/{lesson_id}/content/publish",
    response_model=LessonContentResponse,
    summary="Publish lesson content",
)
async def publish_lesson_content(
    lesson_id: str,
    current_user: User = Depends(require_any_role([UserRole.INSTRUCTOR, UserRole.PLATFORM_ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """
    Mark lesson content as published, making it visible to enrolled students.
    """
    return await content_service.publish_lesson_content(
        db=db,
        lesson_id=lesson_id,
        user=current_user,
    )


@router.post(
    "/{lesson_id}/content/unpublish",
    response_model=LessonContentResponse,
    summary="Unpublish lesson content",
)
async def unpublish_lesson_content(
    lesson_id: str,
    current_user: User = Depends(require_any_role([UserRole.INSTRUCTOR, UserRole.PLATFORM_ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """
    Unpublish lesson content, hiding it from student view.
    """
    return await content_service.unpublish_lesson_content(
        db=db,
        lesson_id=lesson_id,
        user=current_user,
    )
