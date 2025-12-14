import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock, AsyncMock
from uuid import uuid4

from app.main import app
from app.core.deps import get_current_active_user
from app.models.user import User as UserModel


@pytest.mark.asyncio
async def test_get_dashboard_metrics_unauthorized():
    """Test dashboard metrics endpoint returns 403 when no auth provided."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/dashboard/metrics")
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_dashboard_metrics_admin_success():
    """Test dashboard metrics endpoint returns admin cards for admin user."""
    # Mock admin user
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

    # Mock database session with query results
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(side_effect=[
        MagicMock(scalar=lambda: 10),  # total_risks
        MagicMock(scalar=lambda: 15),  # total_controls
        MagicMock(scalar=lambda: 5),  # pending_suggestions
    ])

    # Override dependencies
    app.dependency_overrides[get_current_active_user] = lambda: mock_admin_user
    from app.database import get_async_session
    app.dependency_overrides[get_async_session] = lambda: mock_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/v1/dashboard/metrics")
            assert response.status_code == 200

            data = response.json()
            assert data["user_role"] == "admin"
            assert len(data["cards"]) == 3

            # Verify admin-specific cards
            card_ids = [card["card_id"] for card in data["cards"]]
            assert "system_health" in card_ids
            assert "pending_suggestions" in card_ids
            assert "analyze_document" in card_ids
    finally:
        app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_get_dashboard_metrics_bpo_success():
    """Test dashboard metrics endpoint returns BPO cards for BPO user."""
    # Mock BPO user
    mock_bpo_user = UserModel(
        id=uuid4(),
        email="bpo@example.com",
        hashed_password="mock",
        is_active=True,
        is_superuser=False,
        is_verified=True,
        roles=["bpo"],
        tenant_id=uuid4()
    )

    # Mock database session with query results
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(side_effect=[
        MagicMock(scalar=lambda: 7),  # pending_reviews
        MagicMock(scalar=lambda: 12),  # my_controls
    ])

    # Override dependencies
    app.dependency_overrides[get_current_active_user] = lambda: mock_bpo_user
    from app.database import get_async_session
    app.dependency_overrides[get_async_session] = lambda: mock_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/v1/dashboard/metrics")
            assert response.status_code == 200

            data = response.json()
            assert data["user_role"] == "bpo"
            assert len(data["cards"]) == 3

            # Verify BPO-specific cards
            card_ids = [card["card_id"] for card in data["cards"]]
            assert "pending_reviews" in card_ids
            assert "my_controls" in card_ids
            assert "overdue_assessments" in card_ids

            # Verify pending reviews has urgent status (>5)
            pending_card = next(c for c in data["cards"] if c["card_id"] == "pending_reviews")
            assert pending_card["metric"] == 7
            assert pending_card["status"] == "urgent"
    finally:
        app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_get_dashboard_metrics_executive_success():
    """Test dashboard metrics endpoint returns executive cards for executive user."""
    # Mock executive user
    mock_exec_user = UserModel(
        id=uuid4(),
        email="exec@example.com",
        hashed_password="mock",
        is_active=True,
        is_superuser=False,
        is_verified=True,
        roles=["executive"],
        tenant_id=uuid4()
    )

    # Mock database session with query results
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(side_effect=[
        MagicMock(scalar=lambda: 25),  # total_risks
        MagicMock(scalar=lambda: 10),  # recent_activity
    ])

    # Override dependencies
    app.dependency_overrides[get_current_active_user] = lambda: mock_exec_user
    from app.database import get_async_session
    app.dependency_overrides[get_async_session] = lambda: mock_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/v1/dashboard/metrics")
            assert response.status_code == 200

            data = response.json()
            assert data["user_role"] == "executive"
            assert len(data["cards"]) == 3

            # Verify executive-specific cards
            card_ids = [card["card_id"] for card in data["cards"]]
            assert "risk_overview" in card_ids
            assert "compliance_status" in card_ids
            assert "recent_activity" in card_ids
    finally:
        app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_get_dashboard_metrics_no_tenant():
    """Test dashboard metrics endpoint returns 403 when user has no tenant."""
    # Mock user without tenant
    mock_user_no_tenant = UserModel(
        id=uuid4(),
        email="user@example.com",
        hashed_password="mock",
        is_active=True,
        is_superuser=False,
        is_verified=True,
        roles=["general_user"],
        tenant_id=None  # No tenant assigned
    )

    # Override dependencies
    app.dependency_overrides[get_current_active_user] = lambda: mock_user_no_tenant

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/v1/dashboard/metrics")
            assert response.status_code == 403
            assert "no tenant" in response.json()["detail"].lower()
    finally:
        app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_get_dashboard_metrics_tenant_isolation():
    """Test that dashboard metrics respect tenant isolation."""
    tenant_a_id = uuid4()
    tenant_b_id = uuid4()

    # Mock user from Tenant A
    mock_user_tenant_a = UserModel(
        id=uuid4(),
        email="user_a@example.com",
        hashed_password="mock",
        is_active=True,
        is_superuser=False,
        is_verified=True,
        roles=["general_user"],
        tenant_id=tenant_a_id
    )

    # Mock database session that returns different counts
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(side_effect=[
        MagicMock(scalar=lambda: 5),  # Tenant A: total_risks
        MagicMock(scalar=lambda: 10),  # Tenant A: total_controls
    ])

    # Override dependencies
    app.dependency_overrides[get_current_active_user] = lambda: mock_user_tenant_a
    from app.database import get_async_session
    app.dependency_overrides[get_async_session] = lambda: mock_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/v1/dashboard/metrics")
            assert response.status_code == 200

            data = response.json()
            # Verify tenant A sees their own data
            assert len(data["cards"]) == 2
            risks_card = next(c for c in data["cards"] if c["card_id"] == "total_risks")
            assert risks_card["metric"] == 5
    finally:
        app.dependency_overrides = {}
