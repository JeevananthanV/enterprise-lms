from enum import Enum
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.role import Role
    from app.models.course import Course
    from app.models.enrollment import Enrollment
    from app.models.progress import LessonProgress
    from app.models.quiz import QuizAttempt
    from app.models.notification import Notification
    from app.models.audit import AuditLog
    from app.models.assignment import AssignmentSubmission
    from app.models.certificate import Certificate


class UserRole(str, Enum):
    STUDENT = "STUDENT"
    INSTRUCTOR = "INSTRUCTOR"
    PLATFORM_ADMIN = "PLATFORM_ADMIN"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, native_enum=False),
        default=UserRole.STUDENT,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships with async selectin loading
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users",
        lazy="selectin",
    )
    courses_instructed: Mapped[List["Course"]] = relationship(
        "Course",
        back_populates="instructor",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    enrollments: Mapped[List["Enrollment"]] = relationship(
        "Enrollment",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    lesson_progresses: Mapped[List["LessonProgress"]] = relationship(
        "LessonProgress",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    quiz_attempts: Mapped[List["QuizAttempt"]] = relationship(
        "QuizAttempt",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    assignment_submissions: Mapped[List["AssignmentSubmission"]] = relationship(
        "AssignmentSubmission",
        foreign_keys="[AssignmentSubmission.student_id]",
        back_populates="student",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    certificates: Mapped[List["Certificate"]] = relationship(
        "Certificate",
        back_populates="student",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
