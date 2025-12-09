import pytest
from unittest.mock import patch
from app.models.user import User
from uuid import uuid4
from app.main import app
from app.core.deps import get_current_active_user

@pytest.mark.asyncio
async def test_create_user_endpoint_admin_success(test_client):
    # Mock the user_service.create_user method
    with patch("app.api.v1.endpoints.users.user_service.create_user") as mock_create_user:
        new_user_id = uuid4()
        tenant_id = uuid4()
        
        # The user returned by service
        mock_user = User(
            id=new_user_id,
            email="newbpo@example.com",
            role="bpo",
            tenant_id=tenant_id,
            is_active=True,
            is_verified=True,
            is_superuser=False
        )
        mock_create_user.return_value = mock_user
        
        # The admin user performing the request
        admin_user = User(
            id=uuid4(),
            email="admin@example.com",
            role="admin",
            tenant_id=tenant_id,
            is_active=True
        )

        # Override the dependency to bypass auth
        app.dependency_overrides[get_current_active_user] = lambda: admin_user

        try:
            response = await test_client.post(
                "/api/v1/users",
                json={
                    "email": "newbpo@example.com",
                    "password": "SecurePassword123!",
                    "role": "bpo"
                }
            )

            assert response.status_code == 201
            data = response.json()
            assert data["email"] == "newbpo@example.com"
            assert data["role"] == "bpo"
            assert data["id"] == str(new_user_id)
            
            mock_create_user.assert_called_once()
            
        finally:
            app.dependency_overrides.clear()