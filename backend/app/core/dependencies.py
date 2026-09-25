from typing import Callable, List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import decode_token, is_token_blocklisted
from app.models.user import User, UserRole
from app.repositories.user_repository import user_repository

http_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate JWT token from Bearer header to load active user."""
    if not auth or not auth.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth.credentials
    if await is_token_blocklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_token(token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type for API access.",
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
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive.",
        )

    return user


async def require_authenticated_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency verifying that the request originates from an active authenticated user."""
    return current_user


def require_role(role: UserRole) -> Callable:
    """Factory dependency enforcing a single specific user role."""
    async def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role != role and current_user.role != UserRole.PLATFORM_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires role: {role.value}",
            )
        return current_user

    return role_checker


def require_any_role(roles: List[UserRole]) -> Callable:
    """Factory dependency enforcing that the user has at least one of the permitted roles."""
    async def roles_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in roles and current_user.role != UserRole.PLATFORM_ADMIN:
            allowed_names = [r.value for r in roles]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires one of roles: {', '.join(allowed_names)}",
            )
        return current_user

    return roles_checker


def require_resource_owner_or_admin(resource_owner_id: int, current_user: User) -> None:
    """Helper method verifying that the current user owns the resource or is a Platform Admin."""
    if current_user.id != resource_owner_id and current_user.role != UserRole.PLATFORM_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You do not have permission to access or modify this resource.",
        )
