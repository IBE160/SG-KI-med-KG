from typing import AsyncGenerator
from urllib.parse import urlparse

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .config import settings
from .models import Base, User


# Handle empty or invalid DATABASE_URL
if not settings.DATABASE_URL or settings.DATABASE_URL.strip() == "":
    # Use in-memory SQLite if DATABASE_URL is empty (for tests)
    async_db_connection_url = "sqlite+aiosqlite:///:memory:"
else:
    parsed_db_url = urlparse(settings.DATABASE_URL)

    if parsed_db_url.scheme in ["postgresql", "postgres"]:
        async_db_connection_url = (
            f"postgresql+asyncpg://{parsed_db_url.username}:{parsed_db_url.password}@"
            f"{parsed_db_url.hostname}{':' + str(parsed_db_url.port) if parsed_db_url.port else ''}"
            f"{parsed_db_url.path}"
        )
    elif parsed_db_url.scheme == "sqlite":
        async_db_connection_url = settings.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
    elif parsed_db_url.scheme in ["http", "https"]:
        # If DATABASE_URL is an HTTP(S) URL (like Supabase project URL), use in-memory SQLite
        # This happens when DATABASE_URL is misconfigured - it should be a PostgreSQL connection string
        async_db_connection_url = "sqlite+aiosqlite:///:memory:"
    elif not parsed_db_url.scheme:
        # Empty scheme means invalid URL, use in-memory SQLite
        async_db_connection_url = "sqlite+aiosqlite:///:memory:"
    else:
        async_db_connection_url = settings.DATABASE_URL

# Disable connection pooling for serverless environments like Vercel
engine = create_async_engine(async_db_connection_url, poolclass=NullPool)

async_session_maker = async_sessionmaker(
    engine, expire_on_commit=settings.EXPIRE_ON_COMMIT
)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
