from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.user import User, UserRole


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.email == email.lower().strip()))
        return result.scalars().first()

    async def create_user(
        self,
        db: AsyncSession,
        *,
        email: str,
        hashed_password: str,
        full_name: str,
        role: UserRole = UserRole.STUDENT,
        is_active: bool = True,
    ) -> User:
        user = User(
            email=email.lower().strip(),
            hashed_password=hashed_password,
            full_name=full_name.strip(),
            role=role,
            is_active=is_active,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def list_users(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[User]:
        result = await db.execute(select(User).offset(skip).limit(limit))
        return list(result.scalars().all())


user_repository = UserRepository()
