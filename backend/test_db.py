import asyncio
import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv()

async def test_connection():
    engine = create_async_engine(os.environ["DATABASE_URL"])

    try:
        async with engine.connect():
            print("SQLAlchemy PostgreSQL connection: SUCCESS")
    except Exception as e:
        print("SQLAlchemy PostgreSQL connection: FAILED")
        print(type(e).__name__)
        print(str(e))
    finally:
        await engine.dispose()

asyncio.run(test_connection())