import uuid
from enum import Enum
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Integer, Float, ForeignKey, DateTime, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.course import Course
    from app.models.module import CourseModule
    from app.models.lesson import Lesson


class SubmissionStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    GRADED = "GRADED"
    RESUBMITTED = "RESUBMITTED"


class Assignment(Base, TimestampMixin):
    __tablename__ = "assignments"

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
    module_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("course_modules.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    lesson_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("lessons.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    max_marks: Mapped[int] = mapped_column(
        Integer,
        default=100,
        nullable=False,
    )
    due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    allowed_file_types: Mapped[str] = mapped_column(
        String(255),
        default="pdf,zip,docx,txt,png,jpg",
        nullable=False,
    )
    max_file_size_mb: Mapped[int] = mapped_column(
        Integer,
        default=10,
        nullable=False,
    )
    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    # Relationships
    course: Mapped["Course"] = relationship(
        "Course",
        back_populates="assignments",
        lazy="selectin",
    )
    submissions: Mapped[List["AssignmentSubmission"]] = relationship(
        "AssignmentSubmission",
        back_populates="assignment",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class AssignmentSubmission(Base, TimestampMixin):
    __tablename__ = "assignment_submissions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    assignment_id: Mapped[str] = mapped_column(
        ForeignKey("assignments.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    file_url: Mapped[Optional[str]] = mapped_column(
        String(1024),
        nullable=True,
    )
    file_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    file_size_bytes: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    submission_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    status: Mapped[SubmissionStatus] = mapped_column(
        SQLEnum(SubmissionStatus, native_enum=False),
        default=SubmissionStatus.SUBMITTED,
        index=True,
        nullable=False,
    )
    score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    feedback: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    graded_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    graded_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    assignment: Mapped["Assignment"] = relationship(
        "Assignment",
        back_populates="submissions",
        lazy="selectin",
    )
    student: Mapped["User"] = relationship(
        "User",
        foreign_keys=[student_id],
        back_populates="assignment_submissions",
        lazy="selectin",
    )
