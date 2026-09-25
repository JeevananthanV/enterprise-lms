import asyncio
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import AsyncSessionLocal
from app.models.lesson import Lesson


async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Lesson)
            .options(selectinload(Lesson.quiz))
            .where(
                Lesson.title == "Observability and Monitoring with Prometheus"
            )
        )

        lesson = result.scalars().first()

        if lesson:
            print("LESSON:", lesson.title)
            print("LESSON ID:", lesson.id)
            print("QUIZ OBJECT:", lesson.quiz)

            if lesson.quiz:
                print("QUIZ ID:", lesson.quiz.id)
                print("QUIZ TITLE:", lesson.quiz.title)
            else:
                print("QUIZ ID: None")
        else:
            print("LESSON NOT FOUND")


asyncio.run(main())