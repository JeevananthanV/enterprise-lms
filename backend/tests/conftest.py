import os
import uuid
import pytest
import pytest_asyncio
from typing import Dict, Any, Optional, List
from bson import ObjectId
from httpx import AsyncClient, ASGITransport

TEST_DB_PATH = os.path.abspath("test_enterprise_lms.db")
TEST_DB_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"

os.environ["ENVIRONMENT"] = "test"
os.environ["DEBUG"] = "False"
os.environ["DATABASE_URL"] = TEST_DB_URL

from app.db.session import async_engine, AsyncSessionLocal
from app.models.base import Base
import app.models
from app.db.mongodb import mongodb_manager
from app.main import app


class MockInsertOneResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id


class MockDeleteResult:
    def __init__(self, deleted_count):
        self.deleted_count = deleted_count


class MockAsyncCollection:
    def __init__(self):
        self.docs: Dict[str, Dict[str, Any]] = {}

    def _matches(self, doc: Dict[str, Any], filter_dict: Dict[str, Any]) -> bool:
        if "$or" in filter_dict:
            return any(self._matches(doc, cond) for cond in filter_dict["$or"])
        for k, v in filter_dict.items():
            if k == "_id":
                if str(doc.get("_id")) != str(v):
                    return False
            elif doc.get(k) != v:
                return False
        return True

    async def find_one(self, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for doc in self.docs.values():
            if self._matches(doc, filter_dict):
                return dict(doc)
        return None

    async def insert_one(self, doc: Dict[str, Any]) -> MockInsertOneResult:
        doc_copy = dict(doc)
        if "_id" not in doc_copy:
            doc_copy["_id"] = ObjectId()
        doc_id = str(doc_copy["_id"])
        self.docs[doc_id] = doc_copy
        return MockInsertOneResult(doc_copy["_id"])

    async def find_one_and_update(
        self,
        filter_dict: Dict[str, Any],
        update_dict: Dict[str, Any],
        return_document: bool = True,
    ) -> Optional[Dict[str, Any]]:
        for doc_id, doc in self.docs.items():
            if self._matches(doc, filter_dict):
                if "$set" in update_dict:
                    doc.update(update_dict["$set"])
                if "$inc" in update_dict:
                    for k, v in update_dict["$inc"].items():
                        doc[k] = doc.get(k, 0) + v
                self.docs[doc_id] = doc
                return dict(doc)
        return None

    async def delete_one(self, filter_dict: Dict[str, Any]) -> MockDeleteResult:
        for doc_id, doc in list(self.docs.items()):
            if self._matches(doc, filter_dict):
                del self.docs[doc_id]
                return MockDeleteResult(1)
        return MockDeleteResult(0)

    async def create_indexes(self, indexes: List[Any]) -> List[str]:
        return ["index_created"]


class MockAsyncDatabase:
    def __init__(self):
        self.collections: Dict[str, MockAsyncCollection] = {
            "lesson_contents": MockAsyncCollection()
        }

    def __getitem__(self, name: str) -> MockAsyncCollection:
        if name not in self.collections:
            self.collections[name] = MockAsyncCollection()
        return self.collections[name]


@pytest_asyncio.fixture(autouse=True)
async def setup_mongodb_mock():
    """Ensure an isolated in-memory MongoDB collection for every test."""
    mock_db = MockAsyncDatabase()
    original_db = mongodb_manager.db
    mongodb_manager.db = mock_db
    yield mock_db
    mongodb_manager.db = original_db


@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_test_db():
    """Initialize database tables for the test session."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await async_engine.dispose()
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass


@pytest_asyncio.fixture
async def db_session():
    """Yield an independent async session for direct DB model unit tests."""
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

