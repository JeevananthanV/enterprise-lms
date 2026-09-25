from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.user import User, UserRole
from app.core.dependencies import require_role
from app.schemas.course import (
    CourseCreate,
    CourseUpdate,
    CourseResponse,
    CourseDetailResponse,
    CoursePublishChecklist,
)
from app.schemas.module import (
    ModuleCreate,
    ModuleUpdate,
    ModuleResponse,
    ModuleReorderRequest,
)
from app.schemas.lesson import (
    LessonCreate,
    LessonUpdate,
    LessonResponse,
    LessonReorderRequest,
)
from app.services.course_service import course_service
from app.services.curriculum_service import curriculum_service
from app.repositories.course_repository import course_repository

router = APIRouter()

# Reusable Instructor/Admin authorization dependency
require_instructor = require_role(UserRole.INSTRUCTOR)


# ==============================================================================
# 1. Instructor Course Endpoints
# ==============================================================================

@router.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_in: CourseCreate,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Create a new course in DRAFT status."""
    return await course_service.create_course(db, course_in, current_user)


@router.get("/courses", response_model=List[CourseResponse])
async def list_own_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """List all courses authored by the current instructor (or all for Admin)."""
    courses = await course_service.get_instructor_courses(db, current_user, skip=skip, limit=limit)
    response_items = []
    for c in courses:
        mod_count, les_count = await course_repository.get_counts(db, c.id)
        c_dict = CourseResponse.model_validate(c).model_dump()
        c_dict["module_count"] = mod_count
        c_dict["lesson_count"] = les_count
        response_items.append(CourseResponse(**c_dict))
    return response_items


@router.get("/courses/{course_id}", response_model=CourseDetailResponse)
async def get_own_course(
    course_id: str,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Get full details and syllabus of a specific owned course."""
    course = await course_service.get_course_by_id(db, course_id, current_user)
    mod_count, les_count = await course_repository.get_counts(db, course.id)
    c_dict = CourseDetailResponse.model_validate(course).model_dump()
    c_dict["module_count"] = mod_count
    c_dict["lesson_count"] = les_count
    return CourseDetailResponse(**c_dict)


@router.patch("/courses/{course_id}", response_model=CourseResponse)
@router.put("/courses/{course_id}", response_model=CourseResponse)
async def update_own_course(
    course_id: str,
    course_in: CourseUpdate,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Update metadata for an owned course."""
    return await course_service.update_course(db, course_id, course_in, current_user)


@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_own_course(
    course_id: str,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Delete an owned course and its cascading modules and lessons."""
    await course_service.delete_course(db, course_id, current_user)


@router.get("/courses/{course_id}/publish-checklist", response_model=CoursePublishChecklist)
async def get_publish_checklist(
    course_id: str,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Check whether a course satisfies all prerequisites for publishing."""
    course = await course_service.get_course_by_id(db, course_id, current_user)
    return await course_service.get_publish_checklist(db, course)


@router.post("/courses/{course_id}/publish", response_model=CourseResponse)
async def publish_course(
    course_id: str,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Validate prerequisites and publish the course to the public catalog."""
    return await course_service.publish_course(db, course_id, current_user)


@router.post("/courses/{course_id}/unpublish", response_model=CourseResponse)
async def unpublish_course(
    course_id: str,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Unpublish a course to remove it from the student catalog."""
    return await course_service.unpublish_course(db, course_id, current_user)


@router.get("/courses/{course_id}/preview", response_model=CourseDetailResponse)
async def preview_course(
    course_id: str,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Preview an owned course curriculum in learner mode."""
    course = await course_service.get_course_by_id(db, course_id, current_user)
    mod_count, les_count = await course_repository.get_counts(db, course.id)
    c_dict = CourseDetailResponse.model_validate(course).model_dump()
    c_dict["module_count"] = mod_count
    c_dict["lesson_count"] = les_count
    return CourseDetailResponse(**c_dict)


# ==============================================================================
# 2. Module Management Endpoints
# ==============================================================================

@router.post("/courses/{course_id}/modules", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED)
async def create_module(
    course_id: str,
    module_in: ModuleCreate,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Create a new module within an owned course."""
    return await curriculum_service.create_module(db, course_id, module_in, current_user)


@router.get("/courses/{course_id}/modules", response_model=List[ModuleResponse])
async def list_modules(
    course_id: str,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """List all modules in an owned course."""
    return await curriculum_service.list_modules(db, course_id, current_user)


@router.patch("/modules/{module_id}", response_model=ModuleResponse)
async def update_module(
    module_id: str,
    module_in: ModuleUpdate,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Update a module in an owned course."""
    return await curriculum_service.update_module(db, module_id, module_in, current_user)


@router.delete("/modules/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_module(
    module_id: str,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Delete a module and its cascading lessons."""
    await curriculum_service.delete_module(db, module_id, current_user)


@router.post("/courses/{course_id}/modules/reorder", response_model=List[ModuleResponse])
async def reorder_modules(
    course_id: str,
    body: ModuleReorderRequest,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Reorder modules sequentially within an owned course."""
    return await curriculum_service.reorder_modules(db, course_id, body.module_ids, current_user)


# ==============================================================================
# 3. Lesson Management Endpoints
# ==============================================================================

@router.post("/modules/{module_id}/lessons", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    module_id: str,
    lesson_in: LessonCreate,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Create a new lesson inside an owned module."""
    return await curriculum_service.create_lesson(db, module_id, lesson_in, current_user)


@router.get("/modules/{module_id}/lessons", response_model=List[LessonResponse])
async def list_lessons(
    module_id: str,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """List all lessons within an owned module."""
    return await curriculum_service.list_lessons(db, module_id, current_user)


@router.get("/lessons/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    lesson_id: str,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Get a lesson by ID."""
    return await curriculum_service.get_lesson(db, lesson_id, current_user)


@router.patch("/lessons/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    lesson_id: str,
    lesson_in: LessonUpdate,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Update a lesson in an owned module."""
    return await curriculum_service.update_lesson(db, lesson_id, lesson_in, current_user)


@router.delete("/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(
    lesson_id: str,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Delete a lesson."""
    await curriculum_service.delete_lesson(db, lesson_id, current_user)


@router.post("/modules/{module_id}/lessons/reorder", response_model=List[LessonResponse])
async def reorder_lessons(
    module_id: str,
    body: LessonReorderRequest,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Reorder lessons sequentially within an owned module."""
    return await curriculum_service.reorder_lessons(db, module_id, body.lesson_ids, current_user)
