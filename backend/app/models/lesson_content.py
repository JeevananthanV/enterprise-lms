import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from sqlalchemy import String, Text, Integer, Boolean, ForeignKey, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.lesson import Lesson
    from app.models.course import Course


class LessonContentPG(Base, TimestampMixin):
    """PostgreSQL fallback model for flexible lesson content when MongoDB is disabled/unavailable."""
    __tablename__ = "lesson_contents_pg"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    lesson_id: Mapped[str] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    course_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    content_type: Mapped[str] = mapped_column(
        String(32),
        default="TEXT",
        nullable=False,
    )
    body: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    video_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )
    pdf_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )
    transcript: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )
    external_resources: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSON,
        nullable=True,
    )
    custom_properties: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )
    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    lesson: Mapped["Lesson"] = relationship("Lesson", lazy="selectin")
    course: Mapped[Optional["Course"]] = relationship("Course", lazy="selectin")
