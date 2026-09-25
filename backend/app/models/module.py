import uuid
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Integer, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.lesson import Lesson


class CourseModule(Base, TimestampMixin):
    __tablename__ = "course_modules"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    course_id: Mapped[str] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
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

    # Table constraints
    __table_args__ = (
        UniqueConstraint("course_id", "order_index", name="uq_course_module_order"),
    )

    # Relationships
    course: Mapped["Course"] = relationship(
        "Course",
        back_populates="modules",
        lazy="selectin",
    )
    lessons: Mapped[List["Lesson"]] = relationship(
        "Lesson",
        back_populates="module",
        cascade="all, delete-orphan",
        order_by="Lesson.order_index",
        lazy="selectin",
    )
