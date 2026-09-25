from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.lesson import LessonContentType


class LessonBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    slug: Optional[str] = Field(None, max_length=255)
    content_type: LessonContentType = Field(default=LessonContentType.TEXT)
    content: Optional[str] = None
    duration_minutes: int = Field(default=0, ge=0)
    order_index: Optional[int] = Field(default=1, ge=1)
    is_published: bool = Field(default=True)
    is_free_preview: bool = Field(default=False)


class LessonCreate(LessonBase):
    pass


class LessonUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, max_length=255)
    content_type: Optional[LessonContentType] = None
    content: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=0)
    order_index: Optional[int] = Field(None, ge=1)
    is_published: Optional[bool] = None
    is_free_preview: Optional[bool] = None


class LessonResponse(LessonBase):
    id: str
    module_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LessonReorderRequest(BaseModel):
    lesson_ids: list[str] = Field(min_length=1)
