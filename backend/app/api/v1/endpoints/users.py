from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.dependencies import (
    require_authenticated_user,
    require_role,
    require_any_role,
    require_resource_owner_or_admin,
)
from app.models.user import User, UserRole
from app.repositories.user_repository import user_repository
from app.schemas.user import UserResponse

router = APIRouter()


@router.get(
    "/status",
    summary="Users Domain Status",
)
async def users_domain_status():
    return {"domain": "users", "status": "registered", "phase": "Phase 2"}


@router.get(
    "/admin-only",
    response_model=dict,
    summary="Admin-only restricted resource",
)
async def admin_only_resource(
    current_user: User = Depends(require_role(UserRole.PLATFORM_ADMIN)),
):
    """Resource accessible exclusively to Platform Administrators."""
    return {
        "message": "Welcome to the Administrative Control Layer",
        "user_email": current_user.email,
        "role": current_user.role.value,
    }


@router.get(
    "/instructor-only",
    response_model=dict,
    summary="Instructor-accessible resource",
)
async def instructor_only_resource(
    current_user: User = Depends(
        require_any_role([UserRole.INSTRUCTOR, UserRole.PLATFORM_ADMIN])
    ),
):
    """Resource accessible to Instructors and Platform Administrators."""
    return {
        "message": "Welcome to the Instructor Authoring Suite",
        "user_email": current_user.email,
        "role": current_user.role.value,
    }


@router.get(
    "/student-only",
    response_model=dict,
    summary="Student-accessible resource",
)
async def student_only_resource(
    current_user: User = Depends(
        require_any_role([UserRole.STUDENT, UserRole.PLATFORM_ADMIN])
    ),
):
    """Resource accessible to Students and Platform Administrators."""
    return {
        "message": "Welcome to the Student Learning Portal",
        "user_email": current_user.email,
        "role": current_user.role.value,
    }


@router.get(
    "/{user_id}/profile",
    response_model=UserResponse,
    summary="Get user profile with ownership check",
)
async def get_user_profile_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    """Retrieve user profile enforcing resource ownership or admin privilege."""
    require_resource_owner_or_admin(user_id, current_user)
    user = await user_repository.get(db, user_id)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.get(
    "",
    response_model=List[UserResponse],
    summary="List all users (Admin only)",
)
async def list_users(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.PLATFORM_ADMIN)),
):
    """List system users with pagination, restricted to Platform Admins."""
    return await user_repository.list_users(db, skip=skip, limit=limit)
