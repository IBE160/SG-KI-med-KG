import uuid
from unittest.mock import patch
from datetime import datetime, timedelta, timezone
from jose import jwt

from httpx import AsyncClient, ASGITransport
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.password import PasswordHelper
# Removed: from fastapi_users.authentication import JWTStrategy # Import JWTStrategy

from app.config import settings
from app.models import User, Base

from app.database import get_user_db, get_async_session
from app.main import app
from app.users import get_jwt_strategy, auth_backend # Import auth_backend here


# Removed: @pytest_asyncio.fixture(scope="session", autouse=True)
# Removed: def patch_jwt_strategy_globally():
# Removed:     """Patches get_jwt_strategy globally to ensure a consistent test secret."""
# Removed:     with patch("app.users.get_jwt_strategy") as mock_get_jwt_strategy:
# Removed:         mock_jwt_strategy = JWTStrategy(
# Removed:             secret="test_secret_key_for_jwt_validation_in_tests_fixed",
# Removed:             lifetime_seconds=3600
# Removed:         )
# Removed:         mock_get_jwt_strategy.return_value = mock_jwt_strategy
# Removed:         yield


@pytest_asyncio.fixture(scope="function")
async def engine():
    """Create a fresh test database engine for each test function."""
    # Force in-memory SQLite for isolation to avoid external DB issues
    test_db_url = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(test_db_url, echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(engine):
    """Create a fresh database session for each test."""
    async_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()
        await session.close()


@pytest_asyncio.fixture(scope="function")
async def test_client(db_session):
    """Fixture to create a test client that uses the test database session."""

    # FastAPI-Users database override (wraps session with user operation helpers)
    async def override_get_user_db():
        session = SQLAlchemyUserDatabase(db_session, User)
        try:
            yield session
        finally:
            pass  # We want db_session to be closed by the fixture itself, not dependency

    # General database override (raw session access)
    async def override_get_async_session():
        try:
            yield db_session
        finally:
            pass  # We want db_session to be closed by the fixture itself, not dependency

    # Set up test database overrides
    app.dependency_overrides[get_user_db] = override_get_user_db
    app.dependency_overrides[get_async_session] = override_get_async_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://localhost:8000"
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def authenticated_user(test_client, db_session):
    """Fixture to create and authenticate a test user directly in the database."""

    # Create user data
    user_data = {
        "id": uuid.uuid4(),
        "email": "test@example.com",
        "hashed_password": PasswordHelper().hash("TestPassword123#"),
        "is_active": True,
        "is_superuser": False,
        "is_verified": True,
        "tenant_id": uuid.uuid4(),
    }

    # Create user directly in database
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Generate token using Supabase format (compatible with both)
    settings.SUPABASE_JWT_SECRET = "test-supabase-secret"
    settings.ACCESS_SECRET_KEY = "test-supabase-secret"
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "aud": ["authenticated", "fastapi-users:auth"],
        "iat": now,
        "exp": now + timedelta(hours=1),
        "app_metadata": {
            "role": "general_user",
            "tenant_id": str(user.tenant_id)
        }
    }
    
    access_token = jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")

    # Return both the headers and the user data
    return {
        "headers": {"Authorization": f"Bearer {access_token}"},
        "user": user,
        "user_data": {"email": user_data["email"], "password": "TestPassword123#"},
    }


@pytest_asyncio.fixture(scope="function")
async def superuser_token_headers(test_client, db_session):
    """Fixture to create and authenticate a superuser."""

    # Create user data
    user_data = {
        "id": uuid.uuid4(),
        "email": "admin@example.com",
        "hashed_password": PasswordHelper().hash("AdminPassword123#"),
        "is_active": True,
        "is_superuser": True,
        "is_verified": True,
        "roles": ["admin"],
        "tenant_id": uuid.uuid4(),
    }

    # Create user directly in database
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Generate token using Supabase format (compatible with both)
    settings.SUPABASE_JWT_SECRET = "test-supabase-secret"
    settings.ACCESS_SECRET_KEY = "test-supabase-secret"
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "aud": ["authenticated", "fastapi-users:auth"],
        "iat": now,
        "exp": now + timedelta(hours=1),
        "app_metadata": {
            "roles": user.roles,
            "tenant_id": str(user.tenant_id)
        }
    }
    access_token = jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")

    return {"Authorization": f"Bearer {access_token}"}


@pytest_asyncio.fixture(scope="function")
async def admin_user(db_session):
    """Fixture to create an admin user."""
    user = User(
        id=uuid.uuid4(),
        email="admin_role@example.com",
        hashed_password=PasswordHelper().hash("Password123!"),
        is_active=True,
        is_superuser=False,
        is_verified=True,
        roles=["admin"],
        tenant_id=uuid.uuid4()
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def admin_token_headers(admin_user):
    settings.SUPABASE_JWT_SECRET = "test-supabase-secret"
    settings.ACCESS_SECRET_KEY = "test-supabase-secret"
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(admin_user.id),
        "email": admin_user.email,
        "aud": ["authenticated", "fastapi-users:auth"],
        "iat": now,
        "exp": now + timedelta(hours=1),
        "app_metadata": {
            "roles": admin_user.roles,
            "tenant_id": str(admin_user.tenant_id)
        }
    }
    access_token = jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")
    return {"Authorization": f"Bearer {access_token}"}


@pytest_asyncio.fixture(scope="function")
async def executive_user(db_session):
    """Fixture to create an executive user."""
    user = User(
        id=uuid.uuid4(),
        email="executive@example.com",
        hashed_password=PasswordHelper().hash("Password123!"),
        is_active=True,
        is_superuser=False,
        is_verified=True,
        roles=["executive"],
        tenant_id=uuid.uuid4()
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def executive_token_headers(executive_user):
    settings.SUPABASE_JWT_SECRET = "test-supabase-secret"
    settings.ACCESS_SECRET_KEY = "test-supabase-secret"
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(executive_user.id),
        "email": executive_user.email,
        "aud": ["authenticated", "fastapi-users:auth"],
        "iat": now,
        "exp": now + timedelta(hours=1),
        "app_metadata": {
            "roles": executive_user.roles,
            "tenant_id": str(executive_user.tenant_id)
        }
    }
    access_token = jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")
    return {"Authorization": f"Bearer {access_token}"}


@pytest_asyncio.fixture(scope="function")
async def bpo_user(db_session):
    """Fixture to create a BPO user."""
    user = User(
        id=uuid.uuid4(),
        email="bpo@example.com",
        hashed_password=PasswordHelper().hash("Password123!"),
        is_active=True,
        is_superuser=False,
        is_verified=True,
        roles=["bpo"],
        tenant_id=uuid.uuid4()
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def bpo_token_headers(bpo_user):
    settings.SUPABASE_JWT_SECRET = "test-supabase-secret"
    settings.ACCESS_SECRET_KEY = "test-supabase-secret"
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(bpo_user.id),
        "email": bpo_user.email,
        "aud": ["authenticated", "fastapi-users:auth"],
        "iat": now,
        "exp": now + timedelta(hours=1),
        "app_metadata": {
            "roles": bpo_user.roles,
            "tenant_id": str(bpo_user.tenant_id)
        }
    }
    access_token = jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")
    return {"Authorization": f"Bearer {access_token}"}


@pytest_asyncio.fixture(scope="function")
async def general_user(db_session):
    """Fixture to create a general user."""
    user = User(
        id=uuid.uuid4(),
        email="general@example.com",
        hashed_password=PasswordHelper().hash("Password123!"),
        is_active=True,
        is_superuser=False,
        is_verified=True,
        roles=["general_user"],
        tenant_id=uuid.uuid4()
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def user_token_headers(general_user):
    settings.SUPABASE_JWT_SECRET = "test-supabase-secret"
    settings.ACCESS_SECRET_KEY = "test-supabase-secret"
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(general_user.id),
        "email": general_user.email,
        "aud": ["authenticated", "fastapi-users:auth"],
        "iat": now,
        "exp": now + timedelta(hours=1),
        "app_metadata": {
            "roles": general_user.roles,
            "tenant_id": str(general_user.tenant_id)
        }
    }
    access_token = jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")
    return {"Authorization": f"Bearer {access_token}"}