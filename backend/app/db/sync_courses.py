import asyncio
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.db.session import AsyncSessionLocal
from app.models.course import Course, CourseStatus, CourseLevel
from app.models.module import CourseModule
from app.models.lesson import Lesson, LessonContentType
from app.models.lesson_content import LessonContentPG
from app.models.quiz import Quiz, Question, Answer, QuestionType
from app.models.user import User, UserRole
from app.db.course_data import COURSES_DATA
from app.core.logging import logger


async def sync_all_courses(db: AsyncSession) -> None:
    """
    Synchronizes full structured curriculum, lessons, flexible content,
    and quizzes for all 3 courses into PostgreSQL.
    Preserves existing course IDs and relations.
    """
    # Fetch instructors
    res = await db.execute(select(User).where(User.role == UserRole.INSTRUCTOR))
    instructors = res.scalars().all()
    if not instructors:
        # Fallback to any user
        res = await db.execute(select(User).limit(1))
        default_inst = res.scalars().first()
        inst1 = default_inst
        inst2 = default_inst
    else:
        inst1 = instructors[0]
        inst2 = instructors[1] if len(instructors) > 1 else instructors[0]

    instructor_map = {
        "cloud-architecture-kubernetes-scale": inst1.id if inst1 else 1,
        "modern-full-stack-fastapi-react": inst2.id if inst2 else 1,
        "data-engineering-distributed-systems": inst1.id if inst1 else 1,
    }

    for c_idx, c_data in enumerate(COURSES_DATA, start=1):
        slug = c_data["slug"]
        logger.info(f"--- Synchronizing Course {c_idx}: {c_data['title']} ({slug}) ---")

        # 1. Upsert Course
        res = await db.execute(select(Course).where(Course.slug == slug))
        course = res.scalars().first()

        level_enum = CourseLevel[c_data.get("level", "ADVANCED")]
        if not course:
            course = Course(
                title=c_data["title"],
                slug=slug,
                description=c_data["description"],
                status=CourseStatus.PUBLISHED,
                level=level_enum,
                price=199.99 if level_enum == CourseLevel.ADVANCED else 149.99,
                instructor_id=instructor_map.get(slug, 1),
            )
            db.add(course)
            await db.flush()
            logger.info(f"Created course: {course.title} (ID: {course.id})")
        else:
            course.title = c_data["title"]
            course.description = c_data["description"]
            course.status = CourseStatus.PUBLISHED
            course.level = level_enum
            await db.flush()
            logger.info(f"Updated existing course: {course.title} (ID: {course.id})")

        # 2. Synchronize Modules and Lessons
        for m_idx, m_data in enumerate(c_data["modules"], start=1):
            res = await db.execute(
                select(CourseModule).where(
                    CourseModule.course_id == course.id,
                    CourseModule.order_index == m_data["order_index"]
                )
            )
            module = res.scalars().first()
            if not module:
                module = CourseModule(
                    course_id=course.id,
                    title=m_data["title"],
                    order_index=m_data["order_index"],
                    is_published=True,
                )
                db.add(module)
                await db.flush()
            else:
                module.title = m_data["title"]
                module.is_published = True
                await db.flush()

            last_lesson = None

            # Lessons
            for l_idx, l_data in enumerate(m_data["lessons"], start=1):
                res = await db.execute(
                    select(Lesson).where(
                        Lesson.module_id == module.id,
                        Lesson.order_index == l_data["order_index"]
                    )
                )
                lesson = res.scalars().first()
                lesson_slug = f"{slug}-{l_data['slug']}"

                if not lesson:
                    lesson = Lesson(
                        module_id=module.id,
                        title=l_data["title"],
                        slug=lesson_slug,
                        content_type=l_data["content_type"],
                        content=l_data["content"],
                        duration_minutes=l_data["duration_minutes"],
                        order_index=l_data["order_index"],
                        is_published=True,
                        is_free_preview=l_data.get("is_free_preview", False),
                    )
                    db.add(lesson)
                    await db.flush()
                else:
                    lesson.title = l_data["title"]
                    lesson.slug = lesson_slug
                    lesson.content_type = l_data["content_type"]
                    lesson.content = l_data["content"]
                    lesson.duration_minutes = l_data["duration_minutes"]
                    lesson.is_published = True
                    lesson.is_free_preview = l_data.get("is_free_preview", False)
                    await db.flush()

                last_lesson = lesson

                # Synchronize PostgreSQL fallback flexible content
                res_pg = await db.execute(
                    select(LessonContentPG).where(LessonContentPG.lesson_id == lesson.id)
                )
                content_pg = res_pg.scalars().first()
                if not content_pg:
                    content_pg = LessonContentPG(
                        lesson_id=lesson.id,
                        course_id=course.id,
                        content_type="TEXT",
                        body=l_data["content"],
                        is_published=True,
                        version=1,
                    )
                    db.add(content_pg)
                    await db.flush()
                else:
                    content_pg.body = l_data["content"]
                    content_pg.course_id = course.id
                    content_pg.is_published = True
                    await db.flush()

                if not lesson.content_ref:
                    lesson.content_ref = content_pg.id
                    await db.flush()

            # 3. Synchronize Module Quiz
            if "quiz" in m_data and m_data["quiz"]:
                mq_data = m_data["quiz"]
                res = await db.execute(
                    select(Quiz).where(
                        Quiz.course_id == course.id,
                        Quiz.title == mq_data["title"]
                    )
                )
                quiz = res.scalars().first()
                if not quiz:
                    quiz = Quiz(
                        course_id=course.id,
                        lesson_id=last_lesson.id if last_lesson else None,
                        title=mq_data["title"],
                        description=mq_data["description"],
                        passing_score=mq_data["passing_score"],
                    )
                    db.add(quiz)
                    await db.flush()
                else:
                    quiz.description = mq_data["description"]
                    quiz.passing_score = mq_data["passing_score"]
                    if last_lesson and not quiz.lesson_id:
                        quiz.lesson_id = last_lesson.id
                    await db.flush()

                # Clean and rebuild questions & answers for accuracy
                await db.execute(delete(Question).where(Question.quiz_id == quiz.id))
                await db.flush()

                for q_spec in mq_data["questions"]:
                    question = Question(
                        quiz_id=quiz.id,
                        question_text=q_spec["question_text"],
                        question_type=q_spec["question_type"],
                        points=q_spec["points"],
                        order_index=q_spec["order_index"],
                        explanation=q_spec.get("explanation"),
                    )
                    db.add(question)
                    await db.flush()

                    for a_spec in q_spec["answers"]:
                        answer = Answer(
                            question_id=question.id,
                            answer_text=a_spec["answer_text"],
                            is_correct=a_spec["is_correct"],
                            order_index=a_spec["order_index"],
                        )
                        db.add(answer)
                        await db.flush()

        # 4. Synchronize Final Assessment Quiz
        if "final_quiz" in c_data and c_data["final_quiz"]:
            fq_data = c_data["final_quiz"]
            res = await db.execute(
                select(Quiz).where(
                    Quiz.course_id == course.id,
                    Quiz.title == fq_data["title"]
                )
            )
            quiz = res.scalars().first()
            if not quiz:
                quiz = Quiz(
                    course_id=course.id,
                    lesson_id=None,
                    title=fq_data["title"],
                    description=fq_data["description"],
                    passing_score=fq_data["passing_score"],
                )
                db.add(quiz)
                await db.flush()
            else:
                quiz.description = fq_data["description"]
                quiz.passing_score = fq_data["passing_score"]
                await db.flush()

            # Clean and rebuild questions & answers
            await db.execute(delete(Question).where(Question.quiz_id == quiz.id))
            await db.flush()

            for q_spec in fq_data["questions"]:
                question = Question(
                    quiz_id=quiz.id,
                    question_text=q_spec["question_text"],
                    question_type=q_spec["question_type"],
                    points=q_spec["points"],
                    order_index=q_spec["order_index"],
                    explanation=q_spec.get("explanation"),
                )
                db.add(question)
                await db.flush()

                for a_spec in q_spec["answers"]:
                    answer = Answer(
                        question_id=question.id,
                        answer_text=a_spec["answer_text"],
                        is_correct=a_spec["is_correct"],
                        order_index=a_spec["order_index"],
                    )
                    db.add(answer)
                    await db.flush()

    await db.commit()
    logger.info("Course curriculum and quiz synchronization complete!")


async def main():
    async with AsyncSessionLocal() as session:
        await sync_all_courses(session)


if __name__ == "__main__":
    asyncio.run(main())
