"""Tests for regulatory frameworks endpoints."""
import pytest
from httpx import AsyncClient
from uuid import uuid4
from datetime import datetime, timezone
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.compliance import RegulatoryFramework, RegulatoryRequirement


@pytest.mark.asyncio
async def test_get_regulatory_frameworks_tree_success(
    test_client: AsyncClient,
    admin_user: User,
    admin_token_headers: dict,
    db_session: AsyncSession,
):
    """Test that admin can get regulatory frameworks tree with requirements."""
    now = datetime.now(timezone.utc)

    # Seed: Create framework with requirements
    framework = RegulatoryFramework(
        id=uuid4(),
        tenant_id=admin_user.tenant_id,
        name="GDPR",
        description="General Data Protection Regulation",
        version="2016/679",
        created_at=now,
        updated_at=now
    )
    db_session.add(framework)

    # Create requirements linked to framework
    req1 = RegulatoryRequirement(
        id=uuid4(),
        tenant_id=admin_user.tenant_id,
        framework_id=framework.id,
        name="Article 5 - Principles",
        description="Principles relating to processing of personal data",
        created_at=now,
        updated_at=now
    )
    req2 = RegulatoryRequirement(
        id=uuid4(),
        tenant_id=admin_user.tenant_id,
        framework_id=framework.id,
        name="Article 32 - Security",
        description="Security of processing",
        created_at=now,
        updated_at=now
    )
    db_session.add_all([req1, req2])
    await db_session.commit()

    # Test tree endpoint
    response = await test_client.get(
        "/api/v1/regulatory-frameworks/tree",
        headers=admin_token_headers
    )

    if response.status_code != status.HTTP_200_OK:
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "GDPR"
    assert data[0]["description"] == "General Data Protection Regulation"
    assert data[0]["version"] == "2016/679"
    assert len(data[0]["requirements"]) == 2

    # Verify requirements are included
    req_names = [r["name"] for r in data[0]["requirements"]]
    assert "Article 5 - Principles" in req_names
    assert "Article 32 - Security" in req_names


@pytest.mark.asyncio
async def test_get_regulatory_frameworks_tree_empty(
    test_client: AsyncClient,
    admin_user: User,
    admin_token_headers: dict,
):
    """Test that tree endpoint returns empty list when no frameworks exist."""
    response = await test_client.get(
        "/api/v1/regulatory-frameworks/tree",
        headers=admin_token_headers
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data == []


@pytest.mark.asyncio
async def test_get_regulatory_frameworks_tree_tenant_isolation(
    test_client: AsyncClient,
    admin_user: User,
    admin_token_headers: dict,
    db_session: AsyncSession,
):
    """Test that tree endpoint only returns frameworks for current tenant."""
    now = datetime.now(timezone.utc)

    # Create framework for admin's tenant
    own_framework = RegulatoryFramework(
        id=uuid4(),
        tenant_id=admin_user.tenant_id,
        name="Own Framework",
        description="Framework belonging to admin's tenant",
        created_at=now,
        updated_at=now
    )

    # Create framework for different tenant
    other_tenant_id = uuid4()
    other_framework = RegulatoryFramework(
        id=uuid4(),
        tenant_id=other_tenant_id,
        name="Other Tenant Framework",
        description="Framework belonging to different tenant",
        created_at=now,
        updated_at=now
    )

    db_session.add_all([own_framework, other_framework])
    await db_session.commit()

    response = await test_client.get(
        "/api/v1/regulatory-frameworks/tree",
        headers=admin_token_headers
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Should only see own framework
    assert len(data) == 1
    assert data[0]["name"] == "Own Framework"


@pytest.mark.asyncio
async def test_get_regulatory_frameworks_tree_with_document_link(
    test_client: AsyncClient,
    admin_user: User,
    admin_token_headers: dict,
    db_session: AsyncSession,
):
    """Test that tree endpoint includes document_id when framework is linked to document."""
    now = datetime.now(timezone.utc)
    document_id = uuid4()

    framework = RegulatoryFramework(
        id=uuid4(),
        tenant_id=admin_user.tenant_id,
        name="Linked Framework",
        description="Framework linked to a document",
        document_id=document_id,
        created_at=now,
        updated_at=now
    )
    db_session.add(framework)
    await db_session.commit()

    response = await test_client.get(
        "/api/v1/regulatory-frameworks/tree",
        headers=admin_token_headers
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert len(data) == 1
    assert data[0]["document_id"] == str(document_id)


@pytest.mark.asyncio
async def test_get_regulatory_frameworks_tree_unauthorized(
    test_client: AsyncClient,
):
    """Test that unauthenticated requests are rejected."""
    response = await test_client.get(
        "/api/v1/regulatory-frameworks/tree"
    )

    # FastAPI returns 403 Forbidden for unauthenticated requests with dependency injection
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
