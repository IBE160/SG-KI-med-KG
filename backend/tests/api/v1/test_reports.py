import pytest
from httpx import AsyncClient
from uuid import uuid4
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.compliance import RegulatoryFramework, RegulatoryRequirement, Control
from app.models.mapping import ControlRegulatoryRequirement


@pytest.mark.asyncio
async def test_get_gap_analysis_report_admin(
    test_client: AsyncClient,
    admin_user: User,
    admin_token_headers: dict,
    db_session: AsyncSession,
):
    """Test that Admin can generate a gap analysis report with real DB data."""
    # Seed: Create framework with multiple requirements
    framework = RegulatoryFramework(
        id=uuid4(),
        tenant_id=admin_user.tenant_id,
        name="GDPR Test Framework",
        description="Test regulatory framework",
        version="1.0"
    )
    db_session.add(framework)

    # Create 3 requirements (2 unmapped, 1 mapped)
    req1 = RegulatoryRequirement(
        id=uuid4(),
        tenant_id=admin_user.tenant_id,
        framework_id=framework.id,
        name="Article 5.1",
        description="Requirement 1"
    )
    req2 = RegulatoryRequirement(
        id=uuid4(),
        tenant_id=admin_user.tenant_id,
        framework_id=framework.id,
        name="Article 5.2",
        description="Requirement 2"
    )
    req3 = RegulatoryRequirement(
        id=uuid4(),
        tenant_id=admin_user.tenant_id,
        framework_id=framework.id,
        name="Article 5.3",
        description="Requirement 3 (mapped)"
    )
    db_session.add_all([req1, req2, req3])

    # Create control and map to req3
    control = Control(
        id=uuid4(),
        tenant_id=admin_user.tenant_id,
        name="Test Control",
        description="Control for req3",
        owner_id=admin_user.id
    )
    db_session.add(control)

    mapping = ControlRegulatoryRequirement(
        id=uuid4(),
        tenant_id=admin_user.tenant_id,
        control_id=control.id,
        regulatory_requirement_id=req3.id,
        created_by=admin_user.id
    )
    db_session.add(mapping)
    await db_session.commit()

    # Test gap analysis endpoint
    response = await test_client.get(
        f"/api/v1/reports/gap-analysis/{framework.id}",
        headers=admin_token_headers
    )

    if response.status_code != status.HTTP_200_OK:
        print(f"Error response: {response.text}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Verify aggregated metrics
    assert data["framework_id"] == str(framework.id)
    assert data["framework_name"] == "GDPR Test Framework"
    assert data["total_requirements"] == 3
    assert data["mapped_requirements"] == 1
    assert data["unmapped_requirements"] == 2
    assert data["coverage_percentage"] == pytest.approx(33.33, rel=0.1)

    # Verify gaps list
    assert len(data["gaps"]) == 2
    gap_names = {gap["requirement_name"] for gap in data["gaps"]}
    assert "Article 5.1" in gap_names
    assert "Article 5.2" in gap_names
    assert "Article 5.3" not in gap_names  # Mapped requirement should not be in gaps


@pytest.mark.asyncio
async def test_get_gap_analysis_report_100_percent_coverage(
    test_client: AsyncClient,
    admin_user: User,
    admin_token_headers: dict,
    db_session: AsyncSession,
):
    """Test gap analysis with 100% coverage (all requirements mapped)."""
    framework = RegulatoryFramework(
        id=uuid4(),
        tenant_id=admin_user.tenant_id,
        name="SOC2 Framework",
        description="Fully mapped framework",
        version="1.0"
    )
    db_session.add(framework)

    req = RegulatoryRequirement(
        id=uuid4(),
        tenant_id=admin_user.tenant_id,
        framework_id=framework.id,
        name="CC1.1",
        description="Control environment"
    )
    db_session.add(req)

    control = Control(
        id=uuid4(),
        tenant_id=admin_user.tenant_id,
        name="Control for CC1.1",
        description="Control",
        owner_id=admin_user.id
    )
    db_session.add(control)

    mapping = ControlRegulatoryRequirement(
        id=uuid4(),
        tenant_id=admin_user.tenant_id,
        control_id=control.id,
        regulatory_requirement_id=req.id,
        created_by=admin_user.id
    )
    db_session.add(mapping)
    await db_session.commit()

    response = await test_client.get(
        f"/api/v1/reports/gap-analysis/{framework.id}",
        headers=admin_token_headers
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_requirements"] == 1
    assert data["mapped_requirements"] == 1
    assert data["unmapped_requirements"] == 0
    assert data["coverage_percentage"] == 100.0
    assert len(data["gaps"]) == 0


@pytest.mark.asyncio
async def test_get_gap_analysis_report_framework_not_found(
    test_client: AsyncClient,
    admin_user: User,
    admin_token_headers: dict,
):
    """Test 404 when framework doesn't exist."""
    fake_id = uuid4()
    response = await test_client.get(
        f"/api/v1/reports/gap-analysis/{fake_id}",
        headers=admin_token_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_gap_analysis_report_cross_tenant(
    test_client: AsyncClient,
    admin_user: User,
    admin_token_headers: dict,
    db_session: AsyncSession,
):
    """Test 404 when trying to access another tenant's framework."""
    other_tenant_id = uuid4()
    framework = RegulatoryFramework(
        id=uuid4(),
        tenant_id=other_tenant_id,  # Different tenant
        name="Other Tenant Framework",
        description="Should not be accessible",
        version="1.0"
    )
    db_session.add(framework)
    await db_session.commit()

    response = await test_client.get(
        f"/api/v1/reports/gap-analysis/{framework.id}",
        headers=admin_token_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_gap_analysis_report_bpo_forbidden(
    test_client: AsyncClient,
    bpo_user: User,
    bpo_token_headers: dict,
    db_session: AsyncSession,
):
    """Test that BPO cannot access gap analysis report."""
    framework = RegulatoryFramework(
        id=uuid4(),
        tenant_id=bpo_user.tenant_id,
        name="Test Framework",
        description="Test",
        version="1.0"
    )
    db_session.add(framework)
    await db_session.commit()

    response = await test_client.get(
        f"/api/v1/reports/gap-analysis/{framework.id}",
        headers=bpo_token_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_get_gap_analysis_report_general_forbidden(
    test_client: AsyncClient,
    general_user: User,
    user_token_headers: dict,
    db_session: AsyncSession,
):
    """Test that General User cannot access gap analysis report."""
    framework = RegulatoryFramework(
        id=uuid4(),
        tenant_id=general_user.tenant_id,
        name="Test Framework",
        description="Test",
        version="1.0"
    )
    db_session.add(framework)
    await db_session.commit()

    response = await test_client.get(
        f"/api/v1/reports/gap-analysis/{framework.id}",
        headers=user_token_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_get_gap_analysis_no_auth(
    test_client: AsyncClient,
    db_session: AsyncSession,
):
    """Test that unauthenticated request fails."""
    framework = RegulatoryFramework(
        id=uuid4(),
        tenant_id=uuid4(),
        name="Test Framework",
        description="Test",
        version="1.0"
    )
    db_session.add(framework)
    await db_session.commit()

    response = await test_client.get(f"/api/v1/reports/gap-analysis/{framework.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN
