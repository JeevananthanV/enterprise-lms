import uuid
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class NotificationType(str, Enum):
    SYSTEM = "SYSTEM"
    COURSE = "COURSE"
    ENROLLMENT = "ENROLLMENT"
    GRADE = "GRADE"


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

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
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    notification_type: Mapped[NotificationType] = mapped_column(
        SQLEnum(NotificationType, native_enum=False),
        default=NotificationType.SYSTEM,
        index=True,
        nullable=False,
    )
    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        index=True,
        nullable=False,
    )
    action_url: Mapped[Optional[str]] = mapped_column(
        String(1024),
        nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="notifications",
        lazy="selectin",
    )
