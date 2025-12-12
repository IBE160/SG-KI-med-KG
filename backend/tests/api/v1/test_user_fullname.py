import pytest
from httpx import AsyncClient
import uuid
from app.models.user import User
from fastapi_users.password import PasswordHelper

@pytest.mark.asyncio
async def test_get_me_returns_full_name_none_by_default(test_client, authenticated_user):
    headers = authenticated_user["headers"]
    response = await test_client.get("/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "full_name" in data
    assert data["full_name"] is None

@pytest.mark.asyncio
async def test_get_me_returns_full_name_when_set(test_client, db_session):
    # Create a user with full_name directly in DB
    user_id = uuid.uuid4()
    password_helper = PasswordHelper()
    user = User(
        id=user_id,
        email="fullname@example.com",
        hashed_password=password_helper.hash("testpass"),
        is_active=True,
        is_verified=True,
        full_name="John Doe",
        role="general_user"
    )
    db_session.add(user)
    await db_session.commit()
    
    # Generate token
    from app.users import get_jwt_strategy
    strategy = get_jwt_strategy()
    token = await strategy.write_token(user)
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch user
    response = await test_client.get("/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "fullname@example.com"
    assert data["full_name"] == "John Doe"
