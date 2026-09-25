from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.models.course import Course, CourseStatus
from app.models.lesson import Lesson
from app.models.enrollment import EnrollmentStatus
from app.repositories.course_repository import course_repository
from app.repositories.module_repository import module_repository
from app.repositories.lesson_repository import lesson_repository
from app.repositories.enrollment_repository import enrollment_repository
from app.repositories.progress_repository import progress_repository
from app.schemas.learning import (
    LessonProgressResponse,
    CoursePlayerResponse,
    PlayerModuleItem,
    PlayerLessonItem,
    StudentOverallProgressResponse,
    CourseProgressItem,
)


class ProgressService:
    async def record_lesson_progress(
        self,
        db: AsyncSession,
        user: User,
        lesson_id: str,
        is_completed: bool = True,
    ) -> LessonProgressResponse:
        """Idempotently record and update lesson progress for a student."""
        # 1. Fetch lesson
        lesson = await lesson_repository.get(db, lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found.",
            )

        # 2. Fetch module and course
        module = await module_repository.get(db, lesson.module_id)
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found.",
            )

        course = await course_repository.get(db, module.course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found.",
            )

        # 3. Check access: admin or enrolled student or preview lesson
        is_admin = user.role == UserRole.PLATFORM_ADMIN
        enrollment = await enrollment_repository.get_by_user_and_course(
            db, user_id=user.id, course_id=course.id
        )

        if not is_admin and not enrollment and not lesson.is_free_preview:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be enrolled in this course to track lesson progress.",
            )

        # 4. Upsert lesson progress
        progress = await progress_repository.upsert_lesson_progress(
            db,
            user_id=user.id,
            lesson_id=lesson.id,
            is_completed=is_completed,
        )

        # 5. Recalculate course progress if enrolled
        course_pct = 0.0
        if enrollment:
            mod_count, total_lessons = await course_repository.get_counts(db, course.id)
            completed_ids = await progress_repository.get_completed_lesson_ids_for_course(
                db, user_id=user.id, course_id=course.id
            )
            completed_count = len(completed_ids)

            course_pct = (
                round((completed_count / total_lessons) * 100.0, 1)
                if total_lessons > 0
                else 0.0
            )

            enrollment.progress_percentage = course_pct
            if course_pct >= 100.0:
                enrollment.status = EnrollmentStatus.COMPLETED
                if not enrollment.completed_at:
                    enrollment.completed_at = datetime.now(timezone.utc)
            else:
                enrollment.status = EnrollmentStatus.ACTIVE
                enrollment.completed_at = None

            await enrollment_repository.update(db, enrollment)

        return LessonProgressResponse(
            id=progress.id,
            user_id=progress.user_id,
            lesson_id=progress.lesson_id,
            is_completed=progress.is_completed,
            completed_at=progress.completed_at,
            last_accessed_at=progress.last_accessed_at,
            course_id=course.id,
            course_progress_percentage=course_pct,
        )

    async def get_course_player_data(
        self, db: AsyncSession, user: User, course_id: str
    ) -> CoursePlayerResponse:
        """Fetch course curriculum, lesson content, and student progress for the Course Player."""
        course = await course_repository.get(db, course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found.",
            )

        is_admin = user.role == UserRole.PLATFORM_ADMIN
        if course.status != CourseStatus.PUBLISHED and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course is not published.",
            )

        enrollment = await enrollment_repository.get_by_user_and_course(
            db, user_id=user.id, course_id=course.id
        )

        completed_lesson_ids = set(
            await progress_repository.get_completed_lesson_ids_for_course(
                db, user_id=user.id, course_id=course.id
            )
        )

        all_progress = await progress_repository.get_all_progress_for_user(db, user.id)
        progress_by_lesson_id = {p.lesson_id: p for p in all_progress if p.lesson_id}
        last_accessed_lesson_id = None
        course_progress_records = [
            p for p in all_progress if p.lesson and p.lesson.module and p.lesson.module.course_id == course.id
        ]
        if course_progress_records:
            course_progress_records.sort(key=lambda x: x.last_accessed_at, reverse=True)
            last_accessed_lesson_id = course_progress_records[0].lesson_id

        # Build module and lesson breakdown
        player_modules: List[PlayerModuleItem] = []
        total_lessons = 0

        for m in course.modules:
            if not m.is_published and not is_admin:
                continue

            player_lessons: List[PlayerLessonItem] = []
            for l in m.lessons:
                if not l.is_published and not is_admin:
                    continue

                total_lessons += 1
                is_comp = l.id in completed_lesson_ids
                prog_rec = progress_by_lesson_id.get(l.id)
                quiz_id = l.quiz.id if l.quiz else None

                player_lessons.append(
                    PlayerLessonItem(
                        id=l.id,
                        module_id=l.module_id,
                        title=l.title,
                        slug=l.slug,
                        content_type=l.content_type.value if hasattr(l.content_type, "value") else str(l.content_type),
                        order_index=l.order_index,
                        duration_minutes=l.duration_minutes,
                        is_preview=l.is_free_preview,
                        is_completed=is_comp,
                        completed_at=prog_rec.completed_at if prog_rec else None,
                        content=l.content,
                        quiz_id=quiz_id,
                    )
                )

            player_modules.append(
                PlayerModuleItem(
                    id=m.id,
                    title=m.title,
                    slug=getattr(m, "slug", None),
                    description=m.description,
                    order_index=m.order_index,
                    lessons=player_lessons,
                )
            )

        completed_count = len(completed_lesson_ids)
        progress_pct = (
            round((completed_count / total_lessons) * 100.0, 1)
            if total_lessons > 0
            else 0.0
        )

        instructor_name = course.instructor.full_name if course.instructor else "Enterprise Faculty"

        return CoursePlayerResponse(
            course_id=course.id,
            title=course.title,
            slug=course.slug,
            description=course.description,
            category=course.category,
            level=course.level.value if hasattr(course.level, "value") else str(course.level),
            instructor_name=instructor_name,
            is_enrolled=enrollment is not None and enrollment.status in [EnrollmentStatus.ACTIVE, EnrollmentStatus.COMPLETED],
            enrollment_id=enrollment.id if enrollment else None,
            progress_percentage=progress_pct,
            completed_lessons=completed_count,
            total_lessons=total_lessons,
            last_accessed_lesson_id=last_accessed_lesson_id,
            modules=player_modules,
        )

    async def get_student_overall_progress(
        self, db: AsyncSession, user_id: int
    ) -> StudentOverallProgressResponse:
        """Calculate overall progress analytics for the student progress dashboard."""
        enrollments = await enrollment_repository.list_by_user(db, user_id=user_id)
        all_progress = await progress_repository.get_all_progress_for_user(db, user_id)
        progress_by_course: dict[str, list] = {}
        for p in all_progress:
            if p.lesson and p.lesson.module:
                progress_by_course.setdefault(p.lesson.module.course_id, []).append(p)
        completed_by_course = await progress_repository.get_completed_lesson_ids_by_course(db, user_id)

        course_items: List[CourseProgressItem] = []
        total_completed_lessons = 0
        total_lessons_available = 0
        in_progress_count = 0
        completed_count = 0

        for e in enrollments:
            course = e.course
            if not course:
                continue

            mod_count, les_count = await course_repository.get_counts(db, course.id)
            completed_ids = completed_by_course.get(course.id, set())
            c_completed_lessons = len(completed_ids)

            total_completed_lessons += c_completed_lessons
            total_lessons_available += les_count

            # Recalculate percent
            pct = round((c_completed_lessons / les_count) * 100.0, 1) if les_count > 0 else 0.0

            if pct >= 100.0 or e.status == EnrollmentStatus.COMPLETED:
                completed_count += 1
            else:
                in_progress_count += 1

            c_records = progress_by_course.get(course.id, [])
            last_acc = None
            if c_records:
                c_records.sort(key=lambda x: x.last_accessed_at, reverse=True)
                last_acc = c_records[0].last_accessed_at

            course_items.append(
                CourseProgressItem(
                    course_id=course.id,
                    course_title=course.title,
                    status=e.status,
                    progress_percentage=pct,
                    completed_lessons=c_completed_lessons,
                    total_lessons=les_count,
                    enrolled_at=e.enrolled_at,
                    completed_at=e.completed_at,
                    last_accessed_at=last_acc,
                )
            )

        overall_pct = (
            round((total_completed_lessons / total_lessons_available) * 100.0, 1)
            if total_lessons_available > 0
            else 0.0
        )

        # Recent activity entries
        all_progress.sort(key=lambda x: x.last_accessed_at, reverse=True)
        recent_activity = []
        for p in all_progress[:10]:
            if p.lesson:
                recent_activity.append({
                    "lesson_id": p.lesson_id,
                    "lesson_title": p.lesson.title,
                    "is_completed": p.is_completed,
                    "last_accessed_at": p.last_accessed_at.isoformat(),
                    "course_id": p.lesson.module.course_id if p.lesson.module else None,
                })

        return StudentOverallProgressResponse(
            total_enrolled_courses=len(enrollments),
            in_progress_courses=in_progress_count,
            completed_courses=completed_count,
            overall_completion_percentage=overall_pct,
            total_completed_lessons=total_completed_lessons,
            total_lessons_available=total_lessons_available,
            courses=course_items,
            recent_activity=recent_activity,
        )


progress_service = ProgressService()
