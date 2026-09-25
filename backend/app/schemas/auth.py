from typing import Optional, Any
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.schemas.user import UserResponse
from app.models.user import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    role: UserRole = Field(default=UserRole.STUDENT)

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_upper = v.strip().upper()
            if v_upper in UserRole.__members__:
                return UserRole[v_upper]
        return v


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = None
