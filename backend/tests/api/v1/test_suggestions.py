from fastapi import FastAPI, BackgroundTasks
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock, AsyncMock, patch
from uuid import uuid4
from app.models.suggestion import SuggestionStatus, SuggestionType
from app.main import app
from app.core.deps import has_role, get_current_active_user
from app.models.user import User as UserModel

@pytest.mark.asyncio
async def test_update_suggestion_status_unauthorized():
    """Test update status endpoint requires auth."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.patch(f"/api/v1/suggestions/{uuid4()}/status", json={"status": "accepted"})
        assert response.status_code == 403

@pytest.mark.asyncio
async def test_update_suggestion_status_transition():
    """Test successful status transition."""
    suggestion_id = uuid4()
    
    # Mock Dependencies
    mock_admin_user = UserModel(
        id=uuid4(),
        email="admin@example.com",
        hashed_password="mock",
        is_active=True,
        is_superuser=True,
        is_verified=True,
        roles=["admin"],
        tenant_id=uuid4()
    )
    
    # Mock DB objects
    mock_suggestion = MagicMock()
    mock_suggestion.id = suggestion_id
    mock_suggestion.status = SuggestionStatus.pending
    mock_suggestion.type = SuggestionType.risk
    mock_suggestion.content = {}
    mock_suggestion.rationale = "test"
    mock_suggestion.source_reference = "ref"
    mock_suggestion.document_id = uuid4()

    # Mock DB Session
    mock_db = AsyncMock()
    mock_db.get.return_value = mock_suggestion
    
    # Override dependencies
    app.dependency_overrides[get_current_active_user] = lambda: mock_admin_user
    from app.database import get_async_session
    app.dependency_overrides[get_async_session] = lambda: mock_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            # Test Accept
            response = await ac.patch(
                f"/api/v1/suggestions/{suggestion_id}/status", 
                json={"status": "pending_review", "bpo_id": str(uuid4())}
            )
            assert response.status_code == 200
            assert mock_suggestion.status == SuggestionStatus.pending_review
            
            # Test invalid transition (from pending_review to something else, if restricted)
            # The endpoint check: if suggestion.status != SuggestionStatus.pending -> 400
            mock_suggestion.status = SuggestionStatus.pending_review
            response = await ac.patch(
                f"/api/v1/suggestions/{suggestion_id}/status", 
                json={"status": "rejected"}
            )
            assert response.status_code == 400

    finally:
        app.dependency_overrides = {}

@pytest.mark.asyncio
async def test_update_suggestion_not_found():
    """Test update for non-existent suggestion."""
    mock_admin_user = UserModel(id=uuid4(), email="admin@example.com", hashed_password="mock", is_active=True, is_superuser=True, is_verified=True, roles=["admin"], tenant_id=uuid4())
    mock_db = AsyncMock()
    mock_db.get.return_value = None
    
    app.dependency_overrides[get_current_active_user] = lambda: mock_admin_user
    from app.database import get_async_session
    app.dependency_overrides[get_async_session] = lambda: mock_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.patch(f"/api/v1/suggestions/{uuid4()}/status", json={"status": "rejected"})
            assert response.status_code == 404
    finally:
        app.dependency_overrides = {}
