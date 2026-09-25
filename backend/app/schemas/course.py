from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.models.course import CourseStatus, CourseLevel
from app.schemas.module import ModuleResponse


class InstructorBrief(BaseModel):
    id: int
    full_name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class CourseBase(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    slug: Optional[str] = Field(None, max_length=255)
    short_description: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    category: str = Field(default="General", max_length=100)
    level: CourseLevel = Field(default=CourseLevel.BEGINNER)
    price: float = Field(default=0.0, ge=0.0)
    thumbnail_url: Optional[str] = Field(None, max_length=1024)
    estimated_duration_minutes: int = Field(default=0, ge=0)


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    slug: Optional[str] = Field(None, max_length=255)
    short_description: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    level: Optional[CourseLevel] = None
    price: Optional[float] = Field(None, ge=0.0)
    thumbnail_url: Optional[str] = Field(None, max_length=1024)
    estimated_duration_minutes: Optional[int] = Field(None, ge=0)
    status: Optional[CourseStatus] = None


class CourseResponse(CourseBase):
    id: str
    instructor_id: int
    status: CourseStatus
    instructor: Optional[InstructorBrief] = None
    module_count: Optional[int] = 0
    lesson_count: Optional[int] = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CourseDetailResponse(CourseResponse):
    modules: List[ModuleResponse] = []


class CourseListResponse(BaseModel):
    items: List[CourseResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class CoursePublishChecklist(BaseModel):
    is_publishable: bool
    has_valid_title: bool
    has_description: bool
    module_count: int
    lesson_count: int
    errors: List[str] = []
