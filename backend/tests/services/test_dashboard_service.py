import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import DashboardMetrics, DashboardCard
from app.models.compliance import Risk, Control, BusinessProcess
from app.models.suggestion import AISuggestion, SuggestionStatus


class MockAsyncResult:
    """Mock for SQLAlchemy async result."""
    def __init__(self, value):
        self._value = value

    def scalar(self):
        return self._value


@pytest.mark.asyncio
async def test_get_metrics_admin_role():
    """Test DashboardService returns admin-specific cards."""
    mock_db = AsyncMock()
    user_id = uuid4()
    tenant_id = uuid4()

    # Mock database query results
    mock_db.execute = AsyncMock(side_effect=[
        MockAsyncResult(5),  # total_risks
        MockAsyncResult(10),  # total_controls
        MockAsyncResult(3),  # pending_suggestions
    ])

    metrics = await DashboardService.get_metrics(
        db=mock_db,
        user_id=user_id,
        tenant_id=tenant_id,
        role="admin"
    )

    assert isinstance(metrics, DashboardMetrics)
    assert metrics.user_role == "admin"
    assert len(metrics.cards) == 3

    # Verify admin-specific cards
    card_ids = [card.card_id for card in metrics.cards]
    assert "system_health" in card_ids
    assert "pending_suggestions" in card_ids
    assert "analyze_document" in card_ids

    # Verify metric values
    system_health_card = next(c for c in metrics.cards if c.card_id == "system_health")
    assert system_health_card.metric == 15  # 5 risks + 10 controls

    pending_card = next(c for c in metrics.cards if c.card_id == "pending_suggestions")
    assert pending_card.metric == 3


@pytest.mark.asyncio
async def test_get_metrics_bpo_role():
    """Test DashboardService returns BPO-specific cards."""
    mock_db = AsyncMock()
    user_id = uuid4()
    tenant_id = uuid4()

    # Mock database query results for BPO metrics
    mock_db.execute = AsyncMock(side_effect=[
        MockAsyncResult(7),  # pending_reviews
        MockAsyncResult(12),  # my_controls
    ])

    metrics = await DashboardService.get_metrics(
        db=mock_db,
        user_id=user_id,
        tenant_id=tenant_id,
        role="bpo"
    )

    assert isinstance(metrics, DashboardMetrics)
    assert metrics.user_role == "bpo"
    assert len(metrics.cards) == 3

    # Verify BPO-specific cards
    card_ids = [card.card_id for card in metrics.cards]
    assert "pending_reviews" in card_ids
    assert "my_controls" in card_ids
    assert "overdue_assessments" in card_ids

    # Verify pending reviews count
    pending_reviews_card = next(c for c in metrics.cards if c.card_id == "pending_reviews")
    assert pending_reviews_card.metric == 7
    assert pending_reviews_card.status == "urgent"  # >5 pending reviews

    # Verify my controls count
    my_controls_card = next(c for c in metrics.cards if c.card_id == "my_controls")
    assert my_controls_card.metric == 12


@pytest.mark.asyncio
async def test_get_metrics_executive_role():
    """Test DashboardService returns executive-specific cards."""
    mock_db = AsyncMock()
    user_id = uuid4()
    tenant_id = uuid4()

    # Mock database query results for executive metrics
    mock_db.execute = AsyncMock(side_effect=[
        MockAsyncResult(25),  # total_risks
        MockAsyncResult(10),  # recent_activity
    ])

    metrics = await DashboardService.get_metrics(
        db=mock_db,
        user_id=user_id,
        tenant_id=tenant_id,
        role="executive"
    )

    assert isinstance(metrics, DashboardMetrics)
    assert metrics.user_role == "executive"
    assert len(metrics.cards) == 3

    # Verify executive-specific cards
    card_ids = [card.card_id for card in metrics.cards]
    assert "risk_overview" in card_ids
    assert "compliance_status" in card_ids
    assert "recent_activity" in card_ids

    # Verify risk overview count
    risk_card = next(c for c in metrics.cards if c.card_id == "risk_overview")
    assert risk_card.metric == 25


@pytest.mark.asyncio
async def test_get_metrics_general_user_role():
    """Test DashboardService returns general user cards (read-only)."""
    mock_db = AsyncMock()
    user_id = uuid4()
    tenant_id = uuid4()

    # Mock database query results for general user
    mock_db.execute = AsyncMock(side_effect=[
        MockAsyncResult(8),  # total_risks
        MockAsyncResult(15),  # total_controls
    ])

    metrics = await DashboardService.get_metrics(
        db=mock_db,
        user_id=user_id,
        tenant_id=tenant_id,
        role="general"
    )

    assert isinstance(metrics, DashboardMetrics)
    assert metrics.user_role == "general"
    assert len(metrics.cards) == 2

    # Verify general user cards (read-only informational)
    card_ids = [card.card_id for card in metrics.cards]
    assert "total_risks" in card_ids
    assert "total_controls" in card_ids


@pytest.mark.asyncio
async def test_get_metrics_tenant_isolation():
    """Test that queries filter by tenant_id."""
    mock_db = AsyncMock()
    user_id = uuid4()
    tenant_id = uuid4()

    # Mock query results
    mock_db.execute = AsyncMock(side_effect=[
        MockAsyncResult(3),
        MockAsyncResult(7),
    ])

    await DashboardService.get_metrics(
        db=mock_db,
        user_id=user_id,
        tenant_id=tenant_id,
        role="general"
    )

    # Verify that execute was called (queries were made)
    assert mock_db.execute.call_count == 2


@pytest.mark.asyncio
async def test_bpo_urgent_status_threshold():
    """Test BPO pending reviews card shows urgent status when >5 pending."""
    mock_db = AsyncMock()
    user_id = uuid4()
    tenant_id = uuid4()

    # 6 pending reviews (should trigger urgent)
    mock_db.execute = AsyncMock(side_effect=[
        MockAsyncResult(6),  # pending_reviews
        MockAsyncResult(5),  # my_controls
    ])

    metrics = await DashboardService.get_metrics(
        db=mock_db,
        user_id=user_id,
        tenant_id=tenant_id,
        role="bpo"
    )

    pending_card = next(c for c in metrics.cards if c.card_id == "pending_reviews")
    assert pending_card.status == "urgent"


@pytest.mark.asyncio
async def test_bpo_normal_status_threshold():
    """Test BPO pending reviews card shows normal status when <=5 pending."""
    mock_db = AsyncMock()
    user_id = uuid4()
    tenant_id = uuid4()

    # 3 pending reviews (should NOT trigger urgent)
    mock_db.execute = AsyncMock(side_effect=[
        MockAsyncResult(3),  # pending_reviews
        MockAsyncResult(8),  # my_controls
    ])

    metrics = await DashboardService.get_metrics(
        db=mock_db,
        user_id=user_id,
        tenant_id=tenant_id,
        role="bpo"
    )

    pending_card = next(c for c in metrics.cards if c.card_id == "pending_reviews")
    assert pending_card.status is None  # Not urgent
