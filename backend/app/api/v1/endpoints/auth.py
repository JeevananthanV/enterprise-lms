from typing import Optional
from fastapi import APIRouter, Depends, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.auth_service import auth_service
from app.core.dependencies import require_authenticated_user
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    LogoutRequest,
)
from app.schemas.user import UserResponse

router = APIRouter()


@router.get(
    "/status",
    summary="Auth Domain Status",
)
async def auth_domain_status():
    return {"domain": "auth", "status": "registered", "phase": "Phase 2"}


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user account",
)
async def register(
    register_in: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """Register a new student, instructor, or platform admin account."""
    return await auth_service.register(db, register_in)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive JWT token pair",
)
async def login(
    login_in: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate with email and password to receive access and refresh tokens."""
    return await auth_service.login(db, login_in)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token using refresh token",
)
async def refresh_token(
    refresh_in: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """Obtain a new access token by presenting a valid refresh token."""
    return await auth_service.refresh(db, refresh_in.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Log out and invalidate active tokens",
)
async def logout(
    logout_in: Optional[LogoutRequest] = None,
    authorization: Optional[str] = Header(None),
):
    """Revoke active JWT access and refresh tokens."""
    access_token = None
    if authorization and authorization.startswith("Bearer "):
        access_token = authorization.split(" ")[1]

    refresh_token = logout_in.refresh_token if logout_in else None
    await auth_service.logout(access_token, refresh_token)
    return {"message": "Successfully logged out. Tokens have been invalidated."}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user profile",
)
async def get_current_user_profile(
    current_user: User = Depends(require_authenticated_user),
):
    """Retrieve profile and role information for the active authenticated user."""
    return current_user
