import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    action: Mapped[str] = mapped_column(
        String(100),
        index=True,
        nullable=False,
    )
    resource_type: Mapped[str] = mapped_column(
        String(100),
        index=True,
        nullable=False,
    )
    resource_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        index=True,
        nullable=True,
    )
    details: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="audit_logs",
        lazy="selectin",
    )
