"""phase_7_lesson_content_ref

Revision ID: a729e1c4b901
Revises: f3118a8b1c4e
Create Date: 2026-09-12 15:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a729e1c4b901'
down_revision: Union[str, Sequence[str], None] = 'f3118a8b1c4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema for Phase 7 MongoDB lesson content linkage."""
    op.add_column('lessons', sa.Column('content_ref', sa.String(length=64), nullable=True))
    op.create_index('ix_lessons_content_ref', 'lessons', ['content_ref'], unique=False)


def downgrade() -> None:
    """Downgrade schema for Phase 7."""
    op.drop_index('ix_lessons_content_ref', table_name='lessons')
    op.drop_column('lessons', 'content_ref')
