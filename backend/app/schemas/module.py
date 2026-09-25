from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.lesson import LessonResponse


class ModuleBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    order_index: Optional[int] = Field(default=1, ge=1)
    is_published: bool = Field(default=True)


class ModuleCreate(ModuleBase):
    pass


class ModuleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    order_index: Optional[int] = Field(None, ge=1)
    is_published: Optional[bool] = None


class ModuleResponse(ModuleBase):
    id: str
    course_id: str
    lessons: List[LessonResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ModuleReorderRequest(BaseModel):
    module_ids: List[str] = Field(min_length=1)
