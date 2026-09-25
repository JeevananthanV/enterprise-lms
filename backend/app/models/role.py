import uuid
from typing import List, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Table, Column, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User

# Association table for User <-> Role (Many-to-Many)
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column(
        "id",
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    ),
    Column(
        "user_id",
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column(
        "role_id",
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column(
        "assigned_at",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    ),
    UniqueConstraint("user_id", "role_id", name="uq_user_role"),
)


class Role(Base, TimestampMixin):
    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    # Relationships
    users: Mapped[List["User"]] = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles",
    )
