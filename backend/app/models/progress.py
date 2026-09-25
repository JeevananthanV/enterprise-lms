import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.lesson import Lesson


class LessonProgress(Base, TimestampMixin):
    __tablename__ = "lesson_progress"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    lesson_id: Mapped[str] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_accessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Table constraints
    __table_args__ = (
        UniqueConstraint("user_id", "lesson_id", name="uq_user_lesson_progress"),
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="lesson_progresses",
        lazy="selectin",
    )
    lesson: Mapped["Lesson"] = relationship(
        "Lesson",
        back_populates="progress_records",
        lazy="selectin",
    )
