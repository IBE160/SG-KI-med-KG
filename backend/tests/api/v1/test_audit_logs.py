import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock, AsyncMock
from uuid import uuid4
from app.main import app
from app.core.deps import has_role, get_current_active_user
from app.models.user import User as UserModel
from app.models.audit_log import AuditLog

@pytest.mark.asyncio
async def test_list_audit_logs_unauthorized():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/audit-logs")
        assert response.status_code == 403

from datetime import datetime

@pytest.mark.asyncio
async def test_list_audit_logs_success():
    # Mock Dependencies
    mock_admin_user = UserModel(
        id=uuid4(),
        email="admin@example.com",
        hashed_password="mock",
        is_active=True,
        is_superuser=True,
        is_verified=True,
        role="admin",
        tenant_id=uuid4()
    )
    
    # Mock Logs
    log_entry = AuditLog(
        id=uuid4(),
        action="UPDATE",
        entity_type="Risk",
        entity_id=uuid4(),
        actor_id=mock_admin_user.id,
        changes={},
        created_at=datetime.utcnow() # Added datetime
    )
    
    mock_db = AsyncMock()
    mock_db.execute.return_value = MagicMock(scalars=lambda: MagicMock(all=lambda: [log_entry]))
    
    # Override
    app.dependency_overrides[get_current_active_user] = lambda: mock_admin_user
    from app.database import get_async_session
    app.dependency_overrides[get_async_session] = lambda: mock_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/v1/audit-logs")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["action"] == "UPDATE"
    finally:
        app.dependency_overrides = {}
