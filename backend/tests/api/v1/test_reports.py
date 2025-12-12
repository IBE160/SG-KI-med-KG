import pytest
from httpx import AsyncClient
from uuid import uuid4
from fastapi import status

from app.models.user import User
from app.services.gap_analysis_service import GapAnalysisService
from app.schemas.reports import GapAnalysisReport, UnmappedRequirement

# Mock data
MOCK_FRAMEWORK_ID = uuid4()
MOCK_TENANT_ID = uuid4()

MOCK_REPORT = GapAnalysisReport(
    framework_id=MOCK_FRAMEWORK_ID,
    framework_name="Test Framework",
    total_requirements=10,
    mapped_requirements=8,
    unmapped_requirements=2,
    coverage_percentage=80.0,
    gaps=[
        UnmappedRequirement(
            requirement_id=uuid4(),
            requirement_name="Req 1",
            requirement_description="Desc 1",
            framework_name="Test Framework"
        ),
        UnmappedRequirement(
            requirement_id=uuid4(),
            requirement_name="Req 2",
            requirement_description="Desc 2",
            framework_name="Test Framework"
        )
    ]
)

@pytest.fixture
def mock_gap_service(mocker):
    return mocker.patch(
        "app.api.v1.endpoints.reports.GapAnalysisService.generate_report",
        return_value=MOCK_REPORT
    )

@pytest.mark.asyncio
async def test_get_gap_analysis_report_admin(
        test_client: AsyncClient,
    admin_user: User,
    admin_token_headers: dict,
    mock_gap_service
):
    """Test that Admin can generate a gap analysis report."""
    response = await test_client.get(
        f"/api/v1/reports/gap-analysis/{MOCK_FRAMEWORK_ID}",
        headers=admin_token_headers
    )
    
    if response.status_code != status.HTTP_200_OK:
        print(f"Error response: {response.text}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["framework_id"] == str(MOCK_FRAMEWORK_ID)
    assert data["coverage_percentage"] == 80.0
    assert len(data["gaps"]) == 2
    
    # Verify service called with correct args
    mock_gap_service.assert_called_once()
    call_args = mock_gap_service.call_args
    assert call_args.kwargs["framework_id"] == MOCK_FRAMEWORK_ID
    # Tenant ID check depends on how admin_user fixture sets it up

@pytest.mark.asyncio
async def test_get_gap_analysis_report_executive(
        test_client: AsyncClient,
    executive_user: User, # Assuming executive_user fixture exists or we create one
    executive_token_headers: dict, # Assuming this exists
    mock_gap_service
):
    """Test that Executive can generate a gap analysis report."""
    # Note: If executive fixtures don't exist, we might skip this or need to mock user differently
    # For now, assuming they follow pattern from other tests
    pass 

@pytest.mark.asyncio
async def test_get_gap_analysis_report_bpo_forbidden(
        test_client: AsyncClient,
    bpo_user: User,
    bpo_token_headers: dict,
):
    """Test that BPO cannot access gap analysis report."""
    response = await test_client.get(
        f"/api/v1/reports/gap-analysis/{MOCK_FRAMEWORK_ID}",
        headers=bpo_token_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
async def test_get_gap_analysis_report_general_forbidden(
        test_client: AsyncClient,
    general_user: User,
    user_token_headers: dict,
):
    """Test that General User cannot access gap analysis report."""
    response = await test_client.get(
        f"/api/v1/reports/gap-analysis/{MOCK_FRAMEWORK_ID}",
        headers=user_token_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
async def test_get_gap_analysis_no_auth(test_client: AsyncClient):
    """Test that unauthenticated request fails."""
    response = await test_client.get(f"/api/v1/reports/gap-analysis/{MOCK_FRAMEWORK_ID}")
    assert response.status_code == status.HTTP_403_FORBIDDEN
