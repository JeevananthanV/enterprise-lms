import uuid
from enum import Enum
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Integer, Float, Boolean, ForeignKey, DateTime, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.course import Course
    from app.models.lesson import Lesson


class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
    SINGLE_CHOICE = "SINGLE_CHOICE"
    TRUE_FALSE = "TRUE_FALSE"


class Quiz(Base, TimestampMixin):
    __tablename__ = "quizzes"

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
    passing_score: Mapped[int] = mapped_column(
        Integer,
        default=70,
        nullable=False,
    )
    time_limit_minutes: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    max_attempts: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    randomize_questions: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Relationships
    course: Mapped["Course"] = relationship(
        "Course",
        back_populates="quizzes",
        lazy="selectin",
    )
    lesson: Mapped[Optional["Lesson"]] = relationship(
        "Lesson",
        back_populates="quiz",
        lazy="selectin",
    )
    questions: Mapped[List["Question"]] = relationship(
        "Question",
        back_populates="quiz",
        cascade="all, delete-orphan",
        order_by="Question.order_index",
        lazy="selectin",
    )
    attempts: Mapped[List["QuizAttempt"]] = relationship(
        "QuizAttempt",
        back_populates="quiz",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class Question(Base, TimestampMixin):
    __tablename__ = "questions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    quiz_id: Mapped[str] = mapped_column(
        ForeignKey("quizzes.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    question_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    question_type: Mapped[QuestionType] = mapped_column(
        SQLEnum(QuestionType, native_enum=False),
        default=QuestionType.SINGLE_CHOICE,
        nullable=False,
    )
    points: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    order_index: Mapped[int] = mapped_column(
        Integer,
        default=1,
        index=True,
        nullable=False,
    )
    explanation: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationships
    quiz: Mapped["Quiz"] = relationship(
        "Quiz",
        back_populates="questions",
        lazy="selectin",
    )
    answers: Mapped[List["Answer"]] = relationship(
        "Answer",
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="Answer.order_index",
        lazy="selectin",
    )


class Answer(Base, TimestampMixin):
    __tablename__ = "answers"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    question_id: Mapped[str] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    answer_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    is_correct: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    order_index: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    # Relationships
    question: Mapped["Question"] = relationship(
        "Question",
        back_populates="answers",
        lazy="selectin",
    )


class QuizAttempt(Base, TimestampMixin):
    __tablename__ = "quiz_attempts"

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
    quiz_id: Mapped[str] = mapped_column(
        ForeignKey("quizzes.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    passed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    attempt_number: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    time_spent_seconds: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    selected_question_ids: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="quiz_attempts",
        lazy="selectin",
    )
    quiz: Mapped["Quiz"] = relationship(
        "Quiz",
        back_populates="attempts",
        lazy="selectin",
    )
