from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    role: UserRole = Field(default=UserRole.STUDENT)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128, description="User password (min 8 chars)")


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8, max_length=128)


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
