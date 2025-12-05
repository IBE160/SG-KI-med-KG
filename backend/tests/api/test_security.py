import pytest
from fastapi import HTTPException, status
from jose import jwt
from app.core.security import get_current_user
from app.config import settings
from unittest.mock import MagicMock

# Mock settings
settings.SUPABASE_JWT_SECRET = "supersecret"


def test_get_current_user_valid_token():
    token_payload = {
        "sub": "123",
        "email": "test@example.com",
        "app_metadata": {"role": "admin", "tenant_id": "uuid-123"},
        "exp": 9999999999,
        "iat": 1000000000,
        "aud": "authenticated",
    }
    token = jwt.encode(token_payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")

    credentials = MagicMock()
    credentials.credentials = token

    user = get_current_user(credentials)

    assert user.sub == "123"
    assert user.email == "test@example.com"
    assert user.role == "admin"
    assert user.tenant_id == "uuid-123"


def test_get_current_user_invalid_token():
    token = "invalid.token.here"
    credentials = MagicMock()
    credentials.credentials = token

    with pytest.raises(HTTPException) as exc:
        get_current_user(credentials)

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user_expired_token():
    token_payload = {
        "sub": "123",
        "exp": 1,  # Expired
        "aud": "authenticated",
    }
    token = jwt.encode(token_payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")

    credentials = MagicMock()
    credentials.credentials = token

    with pytest.raises(HTTPException) as exc:
        get_current_user(credentials)

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
