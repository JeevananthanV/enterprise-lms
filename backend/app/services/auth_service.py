from datetime import timedelta
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    blocklist_token,
    is_token_blocklisted,
)
from app.models.user import User, UserRole
from app.repositories.user_repository import user_repository
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
)
from app.schemas.user import UserResponse


class AuthService:
    async def register(self, db: AsyncSession, register_in: RegisterRequest) -> TokenResponse:
        """Register a new user account with unique email enforcement."""
        existing_user = await user_repository.get_by_email(db, register_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email address already exists.",
            )

        hashed_pwd = hash_password(register_in.password)
        user = await user_repository.create_user(
            db,
            email=register_in.email,
            hashed_password=hashed_pwd,
            full_name=register_in.full_name,
            role=register_in.role,
        )

        access_token = create_access_token(
            subject=user.id,
            role=user.role.value,
        )
        refresh_token = create_refresh_token(
            subject=user.id,
            role=user.role.value,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user),
        )

    async def login(self, db: AsyncSession, login_in: LoginRequest) -> TokenResponse:
        """Authenticate user credentials and issue token pair."""
        user = await user_repository.get_by_email(db, login_in.email)
        if not user or not verify_password(login_in.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive. Please contact support.",
            )

        access_token = create_access_token(
            subject=user.id,
            role=user.role.value,
        )
        refresh_token = create_refresh_token(
            subject=user.id,
            role=user.role.value,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user),
        )

    async def refresh(self, db: AsyncSession, refresh_token_str: str) -> TokenResponse:
        """Issue a new access token from a valid refresh token."""
        if await is_token_blocklisted(refresh_token_str):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            payload = decode_token(refresh_token_str)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type for refresh.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Malformed token payload.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await user_repository.get(db, int(user_id))
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Invalidate old refresh token and generate fresh pair
        await blocklist_token(refresh_token_str, expires_seconds=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400)

        new_access_token = create_access_token(
            subject=user.id,
            role=user.role.value,
        )
        new_refresh_token = create_refresh_token(
            subject=user.id,
            role=user.role.value,
        )

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user),
        )

    async def logout(self, access_token: Optional[str], refresh_token: Optional[str]) -> None:
        """Revoke active tokens and add them to blocklist."""
        if access_token:
            await blocklist_token(access_token, expires_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        if refresh_token:
            await blocklist_token(refresh_token, expires_seconds=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400)


auth_service = AuthService()
