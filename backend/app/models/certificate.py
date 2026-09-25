import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.course import Course
    from app.models.enrollment import Enrollment


class Certificate(Base, TimestampMixin):
    __tablename__ = "certificates"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    certificate_number: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
    )
    enrollment_id: Mapped[str] = mapped_column(
        ForeignKey("enrollments.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    course_id: Mapped[str] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    completion_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    verification_hash: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )
    pdf_url: Mapped[Optional[str]] = mapped_column(
        String(1024),
        nullable=True,
    )

    # Relationships
    student: Mapped["User"] = relationship(
        "User",
        foreign_keys=[student_id],
        back_populates="certificates",
        lazy="selectin",
    )
    course: Mapped["Course"] = relationship(
        "Course",
        foreign_keys=[course_id],
        back_populates="certificates",
        lazy="selectin",
    )
    enrollment: Mapped["Enrollment"] = relationship(
        "Enrollment",
        foreign_keys=[enrollment_id],
        lazy="selectin",
    )
