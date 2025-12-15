import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.models.compliance import BusinessProcess, Risk, Control
from app.models.user import User

@pytest.mark.asyncio
async def test_get_overview_hierarchy(
    client: AsyncClient,
    async_session: AsyncSession,
    test_user: User,
    user_token_headers: dict,
):
    # Setup: Create hierarchy
    tenant_id = test_user.tenant_id
    
    # Process
    proc = BusinessProcess(
        id=uuid4(),
        tenant_id=tenant_id,
        name="Test Process",
        description="Process Desc",
        owner_id=test_user.id
    )
    async_session.add(proc)
    await async_session.flush()
    
    # Controls linked to process
    c1 = Control(
        id=uuid4(),
        tenant_id=tenant_id,
        name="Test Control 1",
        description="Desc 1",
        owner_id=test_user.id,
        process_id=proc.id
    )
    async_session.add(c1)
    
    # Risks linked to process
    r1 = Risk(
        id=uuid4(),
        tenant_id=tenant_id,
        name="Test Risk 1",
        description="Desc 1",
        owner_id=test_user.id,
        process_id=proc.id
    )
    async_session.add(r1)
    
    await async_session.commit()
    
    # Act
    response = await client.get(
        "/api/v1/dashboard/overview",
        headers=user_token_headers
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "processes" in data
    assert len(data["processes"]) >= 1
    
    found_proc = next((p for p in data["processes"] if p["id"] == str(proc.id)), None)
    assert found_proc is not None
    assert found_proc["name"] == "Test Process"
    
    # Check children
    assert len(found_proc["controls"]) == 1
    assert found_proc["controls"][0]["id"] == str(c1.id)
    
    assert len(found_proc["risks"]) == 1
    assert found_proc["risks"][0]["id"] == str(r1.id)

@pytest.mark.asyncio
async def test_get_overview_tenant_isolation(
    client: AsyncClient,
    async_session: AsyncSession,
    test_user: User,
    user_token_headers: dict,
):
    # Setup: Create process in DIFFERENT tenant
    other_tenant_id = uuid4()
    
    proc_other = BusinessProcess(
        id=uuid4(),
        tenant_id=other_tenant_id,
        name="Other Tenant Process",
        description="Should not be seen",
        owner_id=test_user.id # Owner doesn't strictly matter for RLS test logic here if we trust tenant_id check
    )
    async_session.add(proc_other)
    await async_session.commit()
    
    # Act
    response = await client.get(
        "/api/v1/dashboard/overview",
        headers=user_token_headers
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    
    # Should NOT find the other tenant's process
    found = any(p["id"] == str(proc_other.id) for p in data["processes"])
    assert not found
