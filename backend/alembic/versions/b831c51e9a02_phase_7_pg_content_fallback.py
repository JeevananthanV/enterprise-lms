"""phase_7_pg_content_fallback

Revision ID: b831c51e9a02
Revises: a729e1c4b901
Create Date: 2026-09-15 14:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b831c51e9a02'
down_revision: Union[str, Sequence[str], None] = 'a729e1c4b901'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema for PostgreSQL flexible content fallback table."""
    op.create_table(
        'lesson_contents_pg',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('lesson_id', sa.String(length=36), nullable=False),
        sa.Column('course_id', sa.String(length=36), nullable=True),
        sa.Column('content_type', sa.String(length=32), nullable=False, server_default='TEXT'),
        sa.Column('body', sa.Text(), nullable=True),
        sa.Column('video_metadata', sa.JSON(), nullable=True),
        sa.Column('pdf_metadata', sa.JSON(), nullable=True),
        sa.Column('transcript', sa.JSON(), nullable=True),
        sa.Column('external_resources', sa.JSON(), nullable=True),
        sa.Column('custom_properties', sa.JSON(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('lesson_contents_pg', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_lesson_contents_pg_id'), ['id'], unique=False)
        batch_op.create_index(batch_op.f('ix_lesson_contents_pg_lesson_id'), ['lesson_id'], unique=True)
        batch_op.create_index(batch_op.f('ix_lesson_contents_pg_course_id'), ['course_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('lesson_contents_pg', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_lesson_contents_pg_course_id'))
        batch_op.drop_index(batch_op.f('ix_lesson_contents_pg_lesson_id'))
        batch_op.drop_index(batch_op.f('ix_lesson_contents_pg_id'))
    op.drop_table('lesson_contents_pg')
