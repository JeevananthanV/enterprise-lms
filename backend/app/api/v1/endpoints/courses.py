import math
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.course import CourseLevel
from app.core.dependencies import get_current_user, require_any_role
from app.schemas.course import (
    CourseResponse,
    CourseDetailResponse,
    CourseListResponse,
)
from app.schemas.module import ModuleResponse
from app.schemas.learning import EnrollmentResponse, CoursePlayerResponse
from app.services.course_service import course_service
from app.services.enrollment_service import enrollment_service
from app.services.progress_service import progress_service
from app.services.cache_service import cache_service
from app.core.config import settings
from app.repositories.course_repository import course_repository

router = APIRouter()


@router.get("/status")
async def get_courses_status():
    """Domain boundary status check."""
    return {"domain": "courses", "status": "registered"}


@router.get("", response_model=CourseListResponse)
async def list_public_courses(
    search: Optional[str] = Query(None, description="Search term for course title or description"),
    category: Optional[str] = Query(None, description="Filter by course category"),
    level: Optional[CourseLevel] = Query(None, description="Filter by course difficulty level"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(12, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
):
    """
    Public & Student Course Catalog.
    Returns only PUBLISHED courses matching the search and filter criteria with pagination.
    Cached in Redis for high read performance.
    """
    cache_key = cache_service.generate_catalog_key(
        search=search,
        category=category,
        level=level.value if level else None,
        page=page,
        page_size=page_size,
    )
    cached_data = await cache_service.get_cached(cache_key)
    if cached_data is not None:
        return CourseListResponse(**cached_data)

    skip = (page - 1) * page_size
    courses, total = await course_repository.list_published(
        db,
        search=search,
        category=category,
        level=level,
        skip=skip,
        limit=page_size,
    )

    items = []
    for c in courses:
        mod_count, les_count = await course_repository.get_counts(db, c.id)
        c_dict = CourseResponse.model_validate(c).model_dump()
        c_dict["module_count"] = mod_count
        c_dict["lesson_count"] = les_count
        items.append(CourseResponse(**c_dict))

    total_pages = math.ceil(total / page_size) if total > 0 else 1

    result = CourseListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
    await cache_service.set_cached(
        cache_key,
        result.model_dump(mode="json"),
        ttl_seconds=settings.CACHE_COURSE_CATALOG_TTL_SECONDS,
    )
    return result


@router.get("/{course_id}", response_model=CourseDetailResponse)
async def get_course_details(
    course_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed overview and syllabus of a published course.
    Draft/unpublished courses are not exposed.
    Cached in Redis for fast access.
    """
    cache_key = cache_service.generate_course_details_key(course_id)
    cached_data = await cache_service.get_cached(cache_key)
    if cached_data is not None:
        return CourseDetailResponse(**cached_data)

    course = await course_service.get_course_by_id(db, course_id, enforce_published=True)
    mod_count, les_count = await course_repository.get_counts(db, course.id)
    c_dict = CourseDetailResponse.model_validate(course).model_dump()
    c_dict["module_count"] = mod_count
    c_dict["lesson_count"] = les_count
    result = CourseDetailResponse(**c_dict)

    await cache_service.set_cached(
        cache_key,
        result.model_dump(mode="json"),
        ttl_seconds=settings.CACHE_COURSE_DETAILS_TTL_SECONDS,
    )
    return result


@router.get("/{course_id}/curriculum", response_model=List[ModuleResponse])
async def get_course_curriculum(
    course_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get the published curriculum and module breakdown for a course.
    Cached in Redis.
    """
    cache_key = cache_service.generate_course_curriculum_key(course_id)
    cached_data = await cache_service.get_cached(cache_key)
    if cached_data is not None:
        return [ModuleResponse(**m) for m in cached_data]

    course = await course_service.get_course_by_id(db, course_id, enforce_published=True)
    published_modules = []
    for m in course.modules:
        if m.is_published:
            m_dict = ModuleResponse.model_validate(m).model_dump()
            m_dict["lessons"] = [l for l in m_dict.get("lessons", []) if l.get("is_published", True)]
            published_modules.append(ModuleResponse(**m_dict))

    await cache_service.set_cached(
        cache_key,
        [m.model_dump(mode="json") for m in published_modules],
        ttl_seconds=settings.CACHE_COURSE_DETAILS_TTL_SECONDS,
    )
    return published_modules



@router.post("/{course_id}/enroll", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def enroll_in_course(
    course_id: str,
    current_user: User = Depends(require_any_role([UserRole.STUDENT, UserRole.PLATFORM_ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """
    Enroll the authenticated student into a course.
    Prevents duplicate enrollments and rejects unauthorized roles.
    """
    enrollment = await enrollment_service.enroll_student(
        db, user=current_user, course_id=course_id
    )
    return enrollment


@router.get("/{course_id}/player", response_model=CoursePlayerResponse)
async def get_course_player_view(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get course player curriculum and student-specific lesson completion states.
    """
    return await progress_service.get_course_player_data(
        db, user=current_user, course_id=course_id
    )

