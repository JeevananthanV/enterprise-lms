import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.db.mongodb import get_content_collection, is_mongodb_available
from app.models.lesson_content import LessonContentPG
from app.core.logging import logger


class ContentRepository:
    """
    Dual-engine Repository for lesson content.
    - Uses MongoDB collection `lesson_contents` when MongoDB is available and enabled.
    - Seamlessly falls back to PostgreSQL table `lesson_contents_pg` when MongoDB is disabled or offline.
    """

    def _format_mongo_doc(self, doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not doc:
            return None
        doc = dict(doc)
        if "_id" in doc:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
        elif "id" not in doc:
            doc["id"] = str(uuid.uuid4())
        return doc

    def _format_pg_model(self, model: Optional[LessonContentPG]) -> Optional[Dict[str, Any]]:
        if not model:
            return None
        return {
            "id": model.id,
            "lesson_id": model.lesson_id,
            "course_id": model.course_id,
            "content_type": model.content_type,
            "body": model.body,
            "video_metadata": model.video_metadata,
            "pdf_metadata": model.pdf_metadata,
            "transcript": model.transcript,
            "external_resources": model.external_resources or [],
            "custom_properties": model.custom_properties or {},
            "version": model.version,
            "is_published": model.is_published,
            "published_at": model.published_at,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
        }

    async def get_by_lesson_id(self, db: Optional[AsyncSession], lesson_id: str) -> Optional[Dict[str, Any]]:
        col = get_content_collection()
        if col is not None:
            try:
                doc = await col.find_one({"lesson_id": lesson_id})
                return self._format_mongo_doc(doc)
            except Exception as e:
                logger.debug(f"MongoDB query failed, attempting PostgreSQL fallback: {e}")

        # PostgreSQL Fallback
        if db is not None:
            res = await db.execute(select(LessonContentPG).where(LessonContentPG.lesson_id == lesson_id))
            pg_model = res.scalars().first()
            return self._format_pg_model(pg_model)
        return None

    async def get_by_id(self, db: Optional[AsyncSession], content_id: str) -> Optional[Dict[str, Any]]:
        col = get_content_collection()
        if col is not None:
            try:
                query: Dict[str, Any]
                if ObjectId.is_valid(content_id):
                    query = {"$or": [{"_id": ObjectId(content_id)}, {"_id": content_id}, {"id": content_id}]}
                else:
                    query = {"$or": [{"_id": content_id}, {"id": content_id}]}
                doc = await col.find_one(query)
                return self._format_mongo_doc(doc)
            except Exception as e:
                logger.debug(f"MongoDB query failed, attempting PostgreSQL fallback: {e}")

        # PostgreSQL Fallback
        if db is not None:
            res = await db.execute(select(LessonContentPG).where(LessonContentPG.id == content_id))
            pg_model = res.scalars().first()
            return self._format_pg_model(pg_model)
        return None

    async def create_content(self, db: Optional[AsyncSession], data: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        col = get_content_collection()
        if col is not None:
            try:
                doc_data = {
                    **data,
                    "version": 1,
                    "created_at": now,
                    "updated_at": now,
                }
                result = await col.insert_one(doc_data)
                doc_data["id"] = str(result.inserted_id)
                if "_id" in doc_data:
                    del doc_data["_id"]
                return doc_data
            except Exception as e:
                logger.debug(f"MongoDB insert failed, attempting PostgreSQL fallback: {e}")

        # PostgreSQL Fallback
        if db is None:
            raise RuntimeError("Database session required for PostgreSQL content fallback")

        pg_model = LessonContentPG(
            id=str(uuid.uuid4()),
            lesson_id=data["lesson_id"],
            course_id=data.get("course_id"),
            content_type=data.get("content_type", "TEXT"),
            body=data.get("body"),
            video_metadata=data.get("video_metadata"),
            pdf_metadata=data.get("pdf_metadata"),
            transcript=data.get("transcript"),
            external_resources=data.get("external_resources"),
            custom_properties=data.get("custom_properties"),
            version=1,
            is_published=data.get("is_published", False),
            published_at=data.get("published_at"),
            created_at=now,
            updated_at=now,
        )
        db.add(pg_model)
        await db.commit()
        await db.refresh(pg_model)
        return self._format_pg_model(pg_model)

    async def update_content(
        self, db: Optional[AsyncSession], lesson_id: str, updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        col = get_content_collection()
        if col is not None:
            try:
                update_doc: Dict[str, Any] = {
                    "$set": {
                        **updates,
                        "updated_at": now,
                    },
                    "$inc": {
                        "version": 1,
                    },
                }
                updated = await col.find_one_and_update(
                    {"lesson_id": lesson_id},
                    update_doc,
                    return_document=True,
                )
                return self._format_mongo_doc(updated)
            except Exception as e:
                logger.debug(f"MongoDB update failed, attempting PostgreSQL fallback: {e}")

        # PostgreSQL Fallback
        if db is None:
            raise RuntimeError("Database session required for PostgreSQL content fallback")

        res = await db.execute(select(LessonContentPG).where(LessonContentPG.lesson_id == lesson_id))
        pg_model = res.scalars().first()
        if not pg_model:
            return None

        for k, v in updates.items():
            if hasattr(pg_model, k):
                setattr(pg_model, k, v)
        pg_model.version += 1
        pg_model.updated_at = now

        await db.commit()
        await db.refresh(pg_model)
        return self._format_pg_model(pg_model)

    async def set_published_status(
        self, db: Optional[AsyncSession], lesson_id: str, is_published: bool
    ) -> Optional[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        col = get_content_collection()
        if col is not None:
            try:
                update_fields: Dict[str, Any] = {
                    "is_published": is_published,
                    "updated_at": now,
                }
                if is_published:
                    update_fields["published_at"] = now
                else:
                    update_fields["published_at"] = None

                updated = await col.find_one_and_update(
                    {"lesson_id": lesson_id},
                    {"$set": update_fields},
                    return_document=True,
                )
                return self._format_mongo_doc(updated)
            except Exception as e:
                logger.debug(f"MongoDB publish update failed, attempting PostgreSQL fallback: {e}")

        # PostgreSQL Fallback
        if db is None:
            raise RuntimeError("Database session required for PostgreSQL content fallback")

        res = await db.execute(select(LessonContentPG).where(LessonContentPG.lesson_id == lesson_id))
        pg_model = res.scalars().first()
        if not pg_model:
            return None

        pg_model.is_published = is_published
        pg_model.published_at = now if is_published else None
        pg_model.updated_at = now

        await db.commit()
        await db.refresh(pg_model)
        return self._format_pg_model(pg_model)

    async def delete_by_lesson_id(self, db: Optional[AsyncSession], lesson_id: str) -> bool:
        col = get_content_collection()
        if col is not None:
            try:
                result = await col.delete_one({"lesson_id": lesson_id})
                return result.deleted_count > 0
            except Exception as e:
                logger.debug(f"MongoDB delete failed, attempting PostgreSQL fallback: {e}")

        if db is not None:
            res = await db.execute(delete(LessonContentPG).where(LessonContentPG.lesson_id == lesson_id))
            await db.commit()
            return res.rowcount > 0
        return False


content_repository = ContentRepository()
