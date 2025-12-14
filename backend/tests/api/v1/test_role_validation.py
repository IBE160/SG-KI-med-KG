"""Tests for role combination validation (Story 2-5 AC 1)."""

import pytest
from uuid import uuid4
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.models.user import User as UserModel
from app.core.deps import get_current_active_user


@pytest.mark.asyncio
async def test_validate_role_combination_general_user_exclusive():
    """Test that general_user cannot be combined with other roles."""
    # Mock admin user
    mock_admin = UserModel(
        id=uuid4(),
        email="admin@example.com",
        hashed_password="mock",
        is_active=True,
        is_superuser=True,
        is_verified=True,
        roles=["admin"],
        tenant_id=uuid4()
    )

    # Override auth dependency
    app.dependency_overrides[get_current_active_user] = lambda: mock_admin

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            # Try to update user with invalid combination
            response = await ac.put(
                f"/api/v1/users/{uuid4()}/roles",
                json={"roles": ["general_user", "admin"]}
            )

            # Should reject with 400
            assert response.status_code == 400
            assert "general_user cannot be combined" in response.json()["detail"]
    finally:
        app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_validate_role_combination_valid_multi_role():
    """Test that valid multi-role combinations are accepted."""
    from app.api.v1.endpoints.users import validate_role_combination

    # Valid combinations
    valid_combos = [
        ["admin"],
        ["bpo"],
        ["executive"],
        ["general_user"],
        ["admin", "bpo"],
        ["admin", "executive"],
        ["bpo", "executive"],
        ["admin", "bpo", "executive"],
    ]

    for combo in valid_combos:
        is_valid, error = validate_role_combination(combo)
        assert is_valid, f"Combination {combo} should be valid, got error: {error}"


@pytest.mark.asyncio
async def test_validate_role_combination_invalid_combinations():
    """Test that invalid role combinations are rejected."""
    from app.api.v1.endpoints.users import validate_role_combination

    # Invalid combinations
    invalid_combos = [
        (["general_user", "admin"], "general_user cannot be combined"),
        (["general_user", "bpo"], "general_user cannot be combined"),
        (["general_user", "executive"], "general_user cannot be combined"),
        (["general_user", "admin", "bpo"], "general_user cannot be combined"),
        (["invalid_role"], "Invalid roles"),
        ([], "At least one role is required"),
    ]

    for combo, expected_error in invalid_combos:
        is_valid, error = validate_role_combination(combo)
        assert not is_valid, f"Combination {combo} should be invalid"
        assert expected_error in error, f"Expected '{expected_error}' in error, got: {error}"


@pytest.mark.asyncio
async def test_create_user_with_invalid_roles():
    """Test that user creation with invalid role combination fails."""
    # Mock admin user
    mock_admin = UserModel(
        id=uuid4(),
        email="admin@example.com",
        hashed_password="mock",
        is_active=True,
        is_superuser=True,
        is_verified=True,
        roles=["admin"],
        tenant_id=uuid4()
    )

    # Override auth dependency
    app.dependency_overrides[get_current_active_user] = lambda: mock_admin

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            # Try to create user with invalid combination
            response = await ac.post(
                "/api/v1/users",
                json={
                    "email": "newuser@example.com",
                    "password": "Test123!@#",
                    "roles": ["general_user", "admin"]
                }
            )

            # Should reject with 400
            assert response.status_code == 400
            assert "general_user cannot be combined" in response.json()["detail"]
    finally:
        app.dependency_overrides = {}
