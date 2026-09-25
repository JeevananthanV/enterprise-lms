import uuid
from enum import Enum
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Integer, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.module import CourseModule
    from app.models.enrollment import Enrollment
    from app.models.quiz import Quiz
    from app.models.assignment import Assignment
    from app.models.certificate import Certificate


class CourseStatus(str, Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    UNPUBLISHED = "UNPUBLISHED"
    ARCHIVED = "ARCHIVED"


class CourseLevel(str, Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"


class Course(Base, TimestampMixin):
    __tablename__ = "courses"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    short_description: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    category: Mapped[str] = mapped_column(
        String(100),
        default="General",
        index=True,
        nullable=False,
    )
    status: Mapped[CourseStatus] = mapped_column(
        SQLEnum(CourseStatus, native_enum=False),
        default=CourseStatus.DRAFT,
        index=True,
        nullable=False,
    )
    level: Mapped[CourseLevel] = mapped_column(
        SQLEnum(CourseLevel, native_enum=False),
        default=CourseLevel.BEGINNER,
        nullable=False,
    )
    estimated_duration_minutes: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    price: Mapped[float] = mapped_column(
        Numeric(10, 2),
        default=0.00,
        nullable=False,
    )
    thumbnail_url: Mapped[Optional[str]] = mapped_column(
        String(1024),
        nullable=True,
    )
    instructor_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    # Relationships
    instructor: Mapped["User"] = relationship(
        "User",
        back_populates="courses_instructed",
        lazy="selectin",
    )
    modules: Mapped[List["CourseModule"]] = relationship(
        "CourseModule",
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="CourseModule.order_index",
        lazy="selectin",
    )
    enrollments: Mapped[List["Enrollment"]] = relationship(
        "Enrollment",
        back_populates="course",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    quizzes: Mapped[List["Quiz"]] = relationship(
        "Quiz",
        back_populates="course",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    assignments: Mapped[List["Assignment"]] = relationship(
        "Assignment",
        back_populates="course",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    certificates: Mapped[List["Certificate"]] = relationship(
        "Certificate",
        back_populates="course",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
