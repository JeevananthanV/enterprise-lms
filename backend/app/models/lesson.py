import uuid
from enum import Enum
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Integer, Boolean, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.module import CourseModule
    from app.models.progress import LessonProgress
    from app.models.quiz import Quiz


class LessonContentType(str, Enum):
    TEXT = "TEXT"
    VIDEO = "VIDEO"
    QUIZ = "QUIZ"
    DOCUMENT = "DOCUMENT"


class Lesson(Base, TimestampMixin):
    __tablename__ = "lessons"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    module_id: Mapped[str] = mapped_column(
        ForeignKey("course_modules.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False,
    )
    content_type: Mapped[LessonContentType] = mapped_column(
        SQLEnum(LessonContentType, native_enum=False),
        default=LessonContentType.TEXT,
        nullable=False,
    )
    content: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    content_ref: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )
    duration_minutes: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    order_index: Mapped[int] = mapped_column(
        Integer,
        default=1,
        index=True,
        nullable=False,
    )
    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_free_preview: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Table constraints
    __table_args__ = (
        UniqueConstraint("module_id", "order_index", name="uq_module_lesson_order"),
    )

    # Relationships
    module: Mapped["CourseModule"] = relationship(
        "CourseModule",
        back_populates="lessons",
        lazy="selectin",
    )
    progress_records: Mapped[List["LessonProgress"]] = relationship(
        "LessonProgress",
        back_populates="lesson",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    quiz: Mapped[Optional["Quiz"]] = relationship(
        "Quiz",
        back_populates="lesson",
        uselist=False,
        lazy="selectin",
    )
