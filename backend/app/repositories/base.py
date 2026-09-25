from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base generic repository for SQLAlchemy ORM operations."""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalars().first()

    async def get_by_id(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        return await self.get(db, id)

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, obj: ModelType) -> ModelType:
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def update(self, db: AsyncSession, obj: ModelType) -> ModelType:
        await db.commit()
        await db.refresh(obj)
        return obj

    async def delete(self, db: AsyncSession, obj: ModelType) -> None:
        await db.delete(obj)
        await db.commit()

