from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.models.course import Course, CourseStatus
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.repositories.enrollment_repository import enrollment_repository
from app.repositories.course_repository import course_repository
from app.repositories.progress_repository import progress_repository
from app.schemas.learning import EnrollmentWithCourseResponse, EnrolledCourseSummary


class EnrollmentService:
    async def enroll_student(
        self, db: AsyncSession, user: User, course_id: str
    ) -> Enrollment:
        """Enroll an authenticated student into a published course."""
        # 1. Fetch course and verify it is published
        course = await course_repository.get(db, course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found.",
            )

        if course.status != CourseStatus.PUBLISHED:
            # Allow admin to enroll in draft courses, but students only published courses
            if user.role != UserRole.PLATFORM_ADMIN:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Course is not published.",
                )

        # 2. Check for duplicate enrollment
        existing = await enrollment_repository.get_by_user_and_course(
            db, user_id=user.id, course_id=course_id
        )
        if existing and existing.status in [EnrollmentStatus.ACTIVE, EnrollmentStatus.COMPLETED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already enrolled in this course.",
            )

        # 3. Create or re-activate enrollment
        now = datetime.now(timezone.utc)
        if existing:
            existing.status = EnrollmentStatus.ACTIVE
            existing.enrolled_at = now
            enrollment = await enrollment_repository.update(db, existing)
        else:
            enrollment = Enrollment(
                user_id=user.id,
                course_id=course_id,
                status=EnrollmentStatus.ACTIVE,
                progress_percentage=0.0,
                enrolled_at=now,
            )
            enrollment = await enrollment_repository.create(db, enrollment)

        return enrollment

    async def get_student_enrollments(
        self, db: AsyncSession, user_id: int
    ) -> List[EnrollmentWithCourseResponse]:
        """Fetch all enrollments for a student with detailed course and progress metrics."""
        enrollments = await enrollment_repository.list_by_user(db, user_id=user_id)
        all_progress = await progress_repository.get_all_progress_for_user(db, user_id)
        progress_by_course: dict[str, list] = {}
        for p in all_progress:
            if p.lesson and p.lesson.module:
                progress_by_course.setdefault(p.lesson.module.course_id, []).append(p)

        completed_by_course = await progress_repository.get_completed_lesson_ids_by_course(db, user_id)
        results = []

        for e in enrollments:
            course = e.course
            if not course:
                continue

            mod_count, les_count = await course_repository.get_counts(db, course.id)
            completed_ids = completed_by_course.get(course.id, set())
            completed_count = len(completed_ids)

            course_lesson_progress = progress_by_course.get(course.id, [])
            last_accessed_lesson_id = None
            if course_lesson_progress:
                course_lesson_progress.sort(key=lambda x: x.last_accessed_at, reverse=True)
                last_accessed_lesson_id = course_lesson_progress[0].lesson_id

            calculated_pct = (
                round((completed_count / les_count) * 100.0, 1) if les_count > 0 else 0.0
            )

            if abs(e.progress_percentage - calculated_pct) > 0.01:
                e.progress_percentage = calculated_pct
                if calculated_pct >= 100.0 and e.status != EnrollmentStatus.COMPLETED:
                    e.status = EnrollmentStatus.COMPLETED
                    e.completed_at = datetime.now(timezone.utc)
                await enrollment_repository.update(db, e)

            instructor_name = "Enterprise Faculty"
            if course.instructor:
                instructor_name = course.instructor.full_name

            course_summary = EnrolledCourseSummary(
                id=course.id,
                title=course.title,
                slug=course.slug,
                short_description=course.short_description,
                category=course.category,
                level=course.level.value if hasattr(course.level, "value") else str(course.level),
                thumbnail_url=course.thumbnail_url,
                instructor_name=instructor_name,
                module_count=mod_count,
                lesson_count=les_count,
                total_duration_minutes=course.estimated_duration_minutes or 0,
            )

            results.append(
                EnrollmentWithCourseResponse(
                    id=e.id,
                    user_id=e.user_id,
                    course_id=e.course_id,
                    status=e.status,
                    progress_percentage=e.progress_percentage,
                    enrolled_at=e.enrolled_at,
                    completed_at=e.completed_at,
                    last_accessed_lesson_id=last_accessed_lesson_id,
                    completed_lesson_count=completed_count,
                    total_lesson_count=les_count,
                    course=course_summary,
                )
            )

        return results

    async def verify_student_course_access(
        self, db: AsyncSession, user: User, course_id: str
    ) -> bool:
        """Verify if user has access to course (either platform admin or actively enrolled student)."""
        if user.role == UserRole.PLATFORM_ADMIN:
            return True

        enrollment = await enrollment_repository.get_by_user_and_course(
            db, user_id=user.id, course_id=course_id
        )
        return enrollment is not None and enrollment.status in [
            EnrollmentStatus.ACTIVE,
            EnrollmentStatus.COMPLETED,
        ]


enrollment_service = EnrollmentService()
