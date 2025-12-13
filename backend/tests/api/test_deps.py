import pytest
from fastapi import HTTPException, status
from app.core.deps import has_role
from app.models.user import User
import uuid


@pytest.mark.asyncio
async def test_has_role_success():
    mock_user = User(id=uuid.uuid4(), email="admin@example.com", roles=["admin"])
    checker = has_role(["admin"])

    result = await checker(mock_user)
    assert result == mock_user


@pytest.mark.asyncio
async def test_has_role_multiple_allowed():
    mock_user = User(id=uuid.uuid4(), email="bpo@example.com", roles=["bpo"])
    checker = has_role(["admin", "bpo"])

    result = await checker(mock_user)
    assert result == mock_user


@pytest.mark.asyncio
async def test_has_role_forbidden():
    mock_user = User(id=uuid.uuid4(), email="user@example.com", roles=["general_user"])
    checker = has_role(["admin"])

    with pytest.raises(HTTPException) as exc:
        await checker(mock_user)

    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
