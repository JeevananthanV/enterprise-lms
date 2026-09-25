import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.user import User, UserRole
from app.models.course import Course, CourseStatus
from app.models.assignment import Assignment, AssignmentSubmission, SubmissionStatus
from app.repositories.assignment_repository import assignment_repository
from app.repositories.course_repository import course_repository
from app.repositories.enrollment_repository import enrollment_repository
from app.schemas.assessment import (
    AssignmentCreate,
    AssignmentResponse,
    AssignmentSubmissionCreate,
    AssignmentSubmissionResponse,
    SubmissionGradeRequest,
)


class AssignmentService:
    def __init__(self):
        pass

    async def create_assignment(
        self,
        db: AsyncSession,
        current_user: User,
        data: AssignmentCreate,
    ) -> AssignmentResponse:
        """Create a new course assignment (Instructor or Admin only)."""
        course = await course_repository.get_by_id(db, data.course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found.",
            )

        # Instructor ownership check
        if current_user.role != UserRole.PLATFORM_ADMIN and course.instructor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to create assignments for this course.",
            )

        assignment = Assignment(
            id=str(uuid.uuid4()),
            course_id=data.course_id,
            module_id=data.module_id,
            lesson_id=data.lesson_id,
            title=data.title,
            description=data.description,
            max_marks=data.max_marks,
            due_date=data.due_date,
            allowed_file_types=data.allowed_file_types,
            max_file_size_mb=data.max_file_size_mb,
            created_by=current_user.id,
        )

        db.add(assignment)
        await db.commit()
        await db.refresh(assignment)

        return AssignmentResponse.model_validate(assignment)

    async def get_assignment(
        self,
        db: AsyncSession,
        current_user: User,
        assignment_id: str,
    ) -> AssignmentResponse:
        """Get assignment details with enrollment/ownership authorization."""
        assignment = await assignment_repository.get_by_id_with_relations(db, assignment_id)
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found.",
            )

        # Students must be enrolled in the course
        if current_user.role == UserRole.STUDENT:
            enrollment = await enrollment_repository.get_by_user_and_course(
                db, current_user.id, assignment.course_id
            )
            if not enrollment:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You must be enrolled in this course to view assignments.",
                )

        return AssignmentResponse.model_validate(assignment)

    async def list_course_assignments(
        self,
        db: AsyncSession,
        current_user: User,
        course_id: str,
    ) -> List[AssignmentResponse]:
        """List all assignments for a course."""
        course = await course_repository.get_by_id(db, course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found.",
            )

        if current_user.role == UserRole.STUDENT:
            enrollment = await enrollment_repository.get_by_user_and_course(
                db, current_user.id, course_id
            )
            if not enrollment:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You must be enrolled to view course assignments.",
                )

        assignments = await assignment_repository.get_by_course(db, course_id)
        return [AssignmentResponse.model_validate(a) for a in assignments]

    # --- Student Submissions ---

    async def submit_assignment(
        self,
        db: AsyncSession,
        current_user: User,
        assignment_id: str,
        data: AssignmentSubmissionCreate,
    ) -> AssignmentSubmissionResponse:
        """Submit or resubmit an assignment."""
        assignment = await assignment_repository.get_by_id_with_relations(db, assignment_id)
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found.",
            )

        enrollment = await enrollment_repository.get_by_user_and_course(
            db, current_user.id, assignment.course_id
        )
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be enrolled in this course to submit assignments.",
            )

        # Check existing submission
        existing = await assignment_repository.get_submission(db, assignment_id, current_user.id)
        now = datetime.now(timezone.utc)

        if existing:
            # Resubmit
            existing.file_url = data.file_url or existing.file_url
            existing.file_name = data.file_name or existing.file_name
            existing.file_size_bytes = data.file_size_bytes or existing.file_size_bytes
            existing.submission_text = data.submission_text or existing.submission_text
            existing.status = SubmissionStatus.RESUBMITTED
            existing.submitted_at = now
            submission = await assignment_repository.update_submission(db, existing)
        else:
            submission = AssignmentSubmission(
                id=str(uuid.uuid4()),
                assignment_id=assignment_id,
                student_id=current_user.id,
                file_url=data.file_url,
                file_name=data.file_name,
                file_size_bytes=data.file_size_bytes,
                submission_text=data.submission_text,
                status=SubmissionStatus.SUBMITTED,
                submitted_at=now,
            )
            submission = await assignment_repository.create_submission(db, submission)

        resp = AssignmentSubmissionResponse.model_validate(submission)
        resp.student_name = current_user.full_name
        resp.student_email = current_user.email
        return resp

    async def get_student_submission(
        self,
        db: AsyncSession,
        current_user: User,
        assignment_id: str,
    ) -> Optional[AssignmentSubmissionResponse]:
        """Get the current student's submission for an assignment."""
        submission = await assignment_repository.get_submission(db, assignment_id, current_user.id)
        if not submission:
            return None

        resp = AssignmentSubmissionResponse.model_validate(submission)
        resp.student_name = current_user.full_name
        resp.student_email = current_user.email
        return resp

    # --- Instructor Grading ---

    async def list_assignment_submissions_for_instructor(
        self,
        db: AsyncSession,
        current_user: User,
        assignment_id: str,
    ) -> List[AssignmentSubmissionResponse]:
        """List all submissions for an assignment with strict instructor ownership checks."""
        assignment = await assignment_repository.get_by_id_with_relations(db, assignment_id)
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found.",
            )

        course = await course_repository.get_by_id(db, assignment.course_id)
        if current_user.role != UserRole.PLATFORM_ADMIN and course.instructor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You do not own this course.",
            )

        submissions = await assignment_repository.list_submissions_for_assignment(db, assignment_id)
        result = []
        for s in submissions:
            item = AssignmentSubmissionResponse.model_validate(s)
            item.student_name = s.student.full_name if s.student else "Student"
            item.student_email = s.student.email if s.student else ""
            result.append(item)
        return result

    async def get_submission_for_instructor(
        self,
        db: AsyncSession,
        current_user: User,
        submission_id: str,
    ) -> AssignmentSubmissionResponse:
        """Get single submission with instructor ownership enforcement."""
        submission = await assignment_repository.get_submission_by_id(db, submission_id)
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found.",
            )

        course_instructor_id = submission.assignment.course.instructor_id
        if current_user.role != UserRole.PLATFORM_ADMIN and course_instructor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You do not own the course this assignment belongs to.",
            )

        resp = AssignmentSubmissionResponse.model_validate(submission)
        resp.student_name = submission.student.full_name if submission.student else "Student"
        resp.student_email = submission.student.email if submission.student else ""
        return resp

    async def grade_submission(
        self,
        db: AsyncSession,
        current_user: User,
        submission_id: str,
        data: SubmissionGradeRequest,
    ) -> AssignmentSubmissionResponse:
        """Grade a student submission (Instructor owner or Admin only)."""
        submission = await assignment_repository.get_submission_by_id(db, submission_id)
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found.",
            )

        course_instructor_id = submission.assignment.course.instructor_id
        if current_user.role != UserRole.PLATFORM_ADMIN and course_instructor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You cannot grade assignments for another instructor's course.",
            )

        max_marks = submission.assignment.max_marks
        if data.score > max_marks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Score cannot exceed maximum marks of {max_marks}.",
            )

        now = datetime.now(timezone.utc)
        submission.score = data.score
        submission.feedback = data.feedback
        submission.graded_by = current_user.id
        submission.graded_at = now
        submission.status = SubmissionStatus.GRADED

        submission = await assignment_repository.update_submission(db, submission)

        resp = AssignmentSubmissionResponse.model_validate(submission)
        resp.student_name = submission.student.full_name if submission.student else "Student"
        resp.student_email = submission.student.email if submission.student else ""
        return resp


assignment_service = AssignmentService()
