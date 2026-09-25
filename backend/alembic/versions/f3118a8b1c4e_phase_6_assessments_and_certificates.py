"""phase_6_assessments_and_certificates

Revision ID: f3118a8b1c4e
Revises: e9000e3bd8c6
Create Date: 2026-09-11 20:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3118a8b1c4e'
down_revision: Union[str, Sequence[str], None] = 'e9000e3bd8c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema for Phase 6 assessments and certificates."""
    # 1. Create assignments table
    op.create_table(
        'assignments',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('course_id', sa.String(length=36), nullable=False),
        sa.Column('module_id', sa.String(length=36), nullable=True),
        sa.Column('lesson_id', sa.String(length=36), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('max_marks', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('allowed_file_types', sa.String(length=255), nullable=False, server_default='pdf,zip,docx,txt,png,jpg'),
        sa.Column('max_file_size_mb', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['module_id'], ['course_modules.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('assignments', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_assignments_id'), ['id'], unique=False)
        batch_op.create_index(batch_op.f('ix_assignments_course_id'), ['course_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_assignments_module_id'), ['module_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_assignments_lesson_id'), ['lesson_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_assignments_created_by'), ['created_by'], unique=False)

    # 2. Create assignment_submissions table
    op.create_table(
        'assignment_submissions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('assignment_id', sa.String(length=36), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('file_url', sa.String(length=1024), nullable=True),
        sa.Column('file_name', sa.String(length=255), nullable=True),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True),
        sa.Column('submission_text', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('SUBMITTED', 'GRADED', 'RESUBMITTED', name='submissionstatus', native_enum=False), nullable=False, server_default='SUBMITTED'),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('graded_by', sa.Integer(), nullable=True),
        sa.Column('graded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['assignment_id'], ['assignments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['graded_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('assignment_submissions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_assignment_submissions_id'), ['id'], unique=False)
        batch_op.create_index(batch_op.f('ix_assignment_submissions_assignment_id'), ['assignment_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_assignment_submissions_student_id'), ['student_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_assignment_submissions_status'), ['status'], unique=False)

    # 3. Create certificates table
    op.create_table(
        'certificates',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('certificate_number', sa.String(length=64), nullable=False),
        sa.Column('enrollment_id', sa.String(length=36), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.String(length=36), nullable=False),
        sa.Column('issued_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('completion_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('verification_hash', sa.String(length=128), nullable=False),
        sa.Column('pdf_url', sa.String(length=1024), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['enrollment_id'], ['enrollments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('certificate_number'),
        sa.UniqueConstraint('enrollment_id')
    )
    with op.batch_alter_table('certificates', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_certificates_id'), ['id'], unique=False)
        batch_op.create_index(batch_op.f('ix_certificates_certificate_number'), ['certificate_number'], unique=True)
        batch_op.create_index(batch_op.f('ix_certificates_enrollment_id'), ['enrollment_id'], unique=True)
        batch_op.create_index(batch_op.f('ix_certificates_verification_hash'), ['verification_hash'], unique=False)

    # 4. Alter quizzes table
    with op.batch_alter_table('quizzes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('randomize_questions', sa.Boolean(), nullable=False, server_default=sa.text('0')))

    # 5. Alter quiz_attempts table
    with op.batch_alter_table('quiz_attempts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('time_spent_seconds', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('selected_question_ids', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('quiz_attempts', schema=None) as batch_op:
        batch_op.drop_column('selected_question_ids')
        batch_op.drop_column('time_spent_seconds')
        batch_op.drop_column('expires_at')

    with op.batch_alter_table('quizzes', schema=None) as batch_op:
        batch_op.drop_column('randomize_questions')

    with op.batch_alter_table('certificates', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_certificates_verification_hash'))
        batch_op.drop_index(batch_op.f('ix_certificates_enrollment_id'))
        batch_op.drop_index(batch_op.f('ix_certificates_certificate_number'))
        batch_op.drop_index(batch_op.f('ix_certificates_id'))
    op.drop_table('certificates')

    with op.batch_alter_table('assignment_submissions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_assignment_submissions_status'))
        batch_op.drop_index(batch_op.f('ix_assignment_submissions_student_id'))
        batch_op.drop_index(batch_op.f('ix_assignment_submissions_assignment_id'))
        batch_op.drop_index(batch_op.f('ix_assignment_submissions_id'))
    op.drop_table('assignment_submissions')

    with op.batch_alter_table('assignments', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_assignments_created_by'))
        batch_op.drop_index(batch_op.f('ix_assignments_lesson_id'))
        batch_op.drop_index(batch_op.f('ix_assignments_module_id'))
        batch_op.drop_index(batch_op.f('ix_assignments_course_id'))
        batch_op.drop_index(batch_op.f('ix_assignments_id'))
    op.drop_table('assignments')
