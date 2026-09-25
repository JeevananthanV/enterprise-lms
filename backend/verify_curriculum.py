import asyncio
from sqlalchemy import select, func
from app.db.session import AsyncSessionLocal
from app.models.course import Course
from app.models.module import CourseModule
from app.models.lesson import Lesson
from app.models.lesson_content import LessonContentPG
from app.models.quiz import Quiz, Question, Answer
from app.models.enrollment import Enrollment


async def verify():
    async with AsyncSessionLocal() as session:
        # Courses
        res = await session.execute(select(Course))
        courses = res.scalars().all()
        print(f"Total Courses: {len(courses)}")
        for c in courses:
            print(f"  - Course [{c.slug}]: {c.title} (Level: {c.level.value}, Status: {c.status.value})")

        # Modules
        res = await session.execute(select(func.count(CourseModule.id)))
        mod_count = res.scalar()
        print(f"\nTotal Modules: {mod_count}")

        # Lessons
        res = await session.execute(select(func.count(Lesson.id)))
        lesson_count = res.scalar()
        print(f"Total Lessons: {lesson_count}")

        # Lesson Contents PG
        res = await session.execute(select(func.count(LessonContentPG.id)))
        pg_content_count = res.scalar()
        print(f"Total PostgreSQL Lesson Content Fallbacks: {pg_content_count}")

        # Quizzes
        res = await session.execute(select(Quiz))
        quizzes = res.scalars().all()
        print(f"\nTotal Quizzes: {len(quizzes)}")
        for q in quizzes:
            res_q = await session.execute(select(func.count(Question.id)).where(Question.quiz_id == q.id))
            q_count = res_q.scalar()
            print(f"  - Quiz: '{q.title}' -> {q_count} questions (Pass score: {q.passing_score}%)")

        # Total Questions & Answers
        res = await session.execute(select(func.count(Question.id)))
        total_questions = res.scalar()
        res = await session.execute(select(func.count(Answer.id)))
        total_answers = res.scalar()
        print(f"\nTotal Questions across all quizzes: {total_questions}")
        print(f"Total Answers across all questions: {total_answers}")

        # Enrollments
        res = await session.execute(select(func.count(Enrollment.id)))
        enrollment_count = res.scalar()
        print(f"Total Active Enrollments: {enrollment_count}")

        # Lesson sample verification
        res = await session.execute(select(Lesson).limit(3))
        sample_lessons = res.scalars().all()
        for sl in sample_lessons:
            assert len(sl.content) > 100, "Lesson content markdown should be populated"
            print(f"Sample Lesson '{sl.title}': content length = {len(sl.content)} chars")

        print("\nAll database curriculum assertions PASSED successfully!")


if __name__ == "__main__":
    asyncio.run(verify())
