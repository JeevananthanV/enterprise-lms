import uuid
from enum import Enum
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Float, ForeignKey, DateTime, Enum as SQLEnum, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.course import Course


class EnrollmentStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    SUSPENDED = "SUSPENDED"


class Enrollment(Base, TimestampMixin):
    __tablename__ = "enrollments"

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
    course_id: Mapped[str] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    status: Mapped[EnrollmentStatus] = mapped_column(
        SQLEnum(EnrollmentStatus, native_enum=False),
        default=EnrollmentStatus.ACTIVE,
        index=True,
        nullable=False,
    )
    progress_percentage: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Table constraints
    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_user_course_enrollment"),
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="enrollments",
        lazy="selectin",
    )
    course: Mapped["Course"] = relationship(
        "Course",
        back_populates="enrollments",
        lazy="selectin",
    )
