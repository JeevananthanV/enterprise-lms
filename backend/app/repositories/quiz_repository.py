from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from app.repositories.base import BaseRepository
from app.models.quiz import Quiz, Question, Answer, QuizAttempt


class QuizRepository(BaseRepository[Quiz]):
    def __init__(self):
        super().__init__(Quiz)

    async def get_with_questions_and_answers(
        self, db: AsyncSession, quiz_id: str
    ) -> Optional[Quiz]:
        """Fetch quiz with all questions and answers loaded."""
        result = await db.execute(
            select(Quiz)
            .options(
                selectinload(Quiz.questions).selectinload(Question.answers),
                selectinload(Quiz.lesson),
                selectinload(Quiz.course),
            )
            .where(Quiz.id == quiz_id)
        )
        return result.scalars().first()

    async def get_by_lesson_id(
        self, db: AsyncSession, lesson_id: str
    ) -> Optional[Quiz]:
        """Fetch quiz linked to a specific lesson."""
        result = await db.execute(
            select(Quiz).where(Quiz.lesson_id == lesson_id)
        )
        return result.scalars().first()

    async def list_attempts_for_user(
        self, db: AsyncSession, user_id: int, quiz_id: str
    ) -> List[QuizAttempt]:
        """List past attempts for a user on a quiz."""
        result = await db.execute(
            select(QuizAttempt)
            .where(
                QuizAttempt.user_id == user_id,
                QuizAttempt.quiz_id == quiz_id,
            )
            .order_by(desc(QuizAttempt.started_at))
        )
        return list(result.scalars().all())

    async def get_attempt_count(
        self, db: AsyncSession, user_id: int, quiz_id: str
    ) -> int:
        """Get total number of attempts a user made for this quiz."""
        result = await db.execute(
            select(QuizAttempt).where(
                QuizAttempt.user_id == user_id,
                QuizAttempt.quiz_id == quiz_id,
            )
        )
        return len(result.scalars().all())

    async def get_attempt_by_id(
        self, db: AsyncSession, attempt_id: str
    ) -> Optional[QuizAttempt]:
        """Fetch attempt by its unique ID."""
        result = await db.execute(
            select(QuizAttempt).where(QuizAttempt.id == attempt_id)
        )
        return result.scalars().first()

    async def update_attempt(
        self, db: AsyncSession, attempt: QuizAttempt
    ) -> QuizAttempt:
        """Update existing attempt."""
        await db.commit()
        await db.refresh(attempt)
        return attempt

    async def create_attempt(
        self, db: AsyncSession, attempt: QuizAttempt
    ) -> QuizAttempt:
        """Store new quiz attempt."""
        db.add(attempt)
        await db.commit()
        await db.refresh(attempt)
        return attempt


quiz_repository = QuizRepository()
