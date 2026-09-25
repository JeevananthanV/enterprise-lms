from typing import Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.user import User
from app.models.course import Course
from app.models.lesson import Lesson
from app.models.progress import LessonProgress
from app.models.quiz import Quiz, QuizAttempt
from app.models.assignment import Assignment, AssignmentSubmission, SubmissionStatus
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.repositories.enrollment_repository import enrollment_repository
from app.repositories.course_repository import course_repository
from app.repositories.certificate_repository import certificate_repository
from app.schemas.assessment import CourseCompletionReport


class CourseCompletionService:
    async def calculate_course_completion(
        self,
        db: AsyncSession,
        student_id: int,
        course_id: str,
    ) -> CourseCompletionReport:
        """
        Calculates authoritative course completion percentage and eligibility for certification.
        A course requires:
        1. All published lessons marked completed (100%).
        2. All required quizzes passed (score >= passing_score).
        3. All assignments graded/passed (if assignments exist).
        """
        enrollment = await enrollment_repository.get_by_user_and_course(db, student_id, course_id)
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student is not enrolled in this course.",
            )

        course = await course_repository.get_by_id(db, course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found.",
            )

        # 1. Lessons check
        published_lessons = []
        for module in course.modules:
            for lesson in module.lessons:
                if lesson.is_published:
                    published_lessons.append(lesson)

        total_lessons = len(published_lessons)
        completed_lessons = 0

        if total_lessons > 0:
            lesson_ids = [l.id for l in published_lessons]
            prog_stmt = select(LessonProgress).where(
                LessonProgress.user_id == student_id,
                LessonProgress.lesson_id.in_(lesson_ids),
                LessonProgress.is_completed == True,
            )
            prog_res = await db.execute(prog_stmt)
            completed_lessons = len(prog_res.scalars().all())

        # 2. Quizzes check
        quizzes = course.quizzes or []
        total_quizzes = len(quizzes)
        passed_quizzes = 0

        if total_quizzes > 0:
            for q in quizzes:
                attempt_stmt = select(QuizAttempt).where(
                    QuizAttempt.user_id == student_id,
                    QuizAttempt.quiz_id == q.id,
                    QuizAttempt.passed == True,
                )
                attempt_res = await db.execute(attempt_stmt)
                if attempt_res.scalars().first():
                    passed_quizzes += 1

        # 3. Assignments check
        assignments = course.assignments or []
        total_assignments = len(assignments)
        graded_assignments = 0

        if total_assignments > 0:
            for a in assignments:
                sub_stmt = select(AssignmentSubmission).where(
                    AssignmentSubmission.assignment_id == a.id,
                    AssignmentSubmission.student_id == student_id,
                    AssignmentSubmission.status == SubmissionStatus.GRADED,
                )
                sub_res = await db.execute(sub_stmt)
                if sub_res.scalars().first():
                    graded_assignments += 1

        # Total evaluation items
        total_items = total_lessons + total_quizzes + total_assignments
        completed_items = completed_lessons + passed_quizzes + graded_assignments

        if total_items == 0:
            completion_percentage = 100.0
            is_completed = True
        else:
            completion_percentage = round((completed_items / total_items) * 100, 1)
            is_completed = (
                (completed_lessons == total_lessons)
                and (passed_quizzes == total_quizzes)
                and (graded_assignments == total_assignments)
            )

        # Update enrollment progress if changed
        if enrollment.progress_percentage != completion_percentage:
            enrollment.progress_percentage = completion_percentage
            if is_completed and enrollment.status != EnrollmentStatus.COMPLETED:
                enrollment.status = EnrollmentStatus.COMPLETED
            await db.commit()
            await db.refresh(enrollment)

        eligible_for_cert = is_completed and completion_percentage >= 100.0

        # Check if certificate exists
        existing_cert = await certificate_repository.get_by_enrollment_id(db, enrollment.id)

        user_stmt = select(User).where(User.id == student_id)
        user_res = await db.execute(user_stmt)
        user = user_res.scalar_one_or_none()
        student_name = user.full_name if user else "Student"

        return CourseCompletionReport(
            course_id=course.id,
            course_title=course.title,
            student_id=student_id,
            student_name=student_name,
            completion_percentage=completion_percentage,
            is_completed=is_completed,
            completed_lessons=completed_lessons,
            total_lessons=total_lessons,
            passed_quizzes=passed_quizzes,
            total_quizzes=total_quizzes,
            graded_assignments=graded_assignments,
            total_assignments=total_assignments,
            eligible_for_certificate=eligible_for_cert,
            certificate_id=existing_cert.id if existing_cert else None,
            certificate_number=existing_cert.certificate_number if existing_cert else None,
        )


course_completion_service = CourseCompletionService()
