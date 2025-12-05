import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_create_control(test_client: AsyncClient, superuser_token_headers):
    response = await test_client.post(
        "/api/v1/controls",
        headers=superuser_token_headers,
        json={
            "name": "Test Control",
            "description": "A test control",
            "type": "Preventive",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Control"
    assert "id" in data


@pytest.mark.anyio
async def test_read_controls(test_client: AsyncClient, superuser_token_headers):
    # Create a control first
    await test_client.post(
        "/api/v1/controls",
        headers=superuser_token_headers,
        json={
            "name": "Test Control List",
            "description": "A test control for list",
            "type": "Preventive",
        },
    )

    response = await test_client.get(
        "/api/v1/controls", headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) > 0


@pytest.mark.anyio
async def test_read_control_by_id(test_client: AsyncClient, superuser_token_headers):
    # Create a control
    create_response = await test_client.post(
        "/api/v1/controls",
        headers=superuser_token_headers,
        json={
            "name": "Test Control ID",
            "description": "A test control for ID",
            "type": "Preventive",
        },
    )
    control_id = create_response.json()["id"]

    response = await test_client.get(
        f"/api/v1/controls/{control_id}", headers=superuser_token_headers
    )
    assert response.status_code == 200
    assert response.json()["id"] == control_id


@pytest.mark.anyio
async def test_update_control(test_client: AsyncClient, superuser_token_headers):
    # Create a control
    create_response = await test_client.post(
        "/api/v1/controls",
        headers=superuser_token_headers,
        json={
            "name": "Test Control Update",
            "description": "A test control for update",
            "type": "Preventive",
        },
    )
    control_id = create_response.json()["id"]

    # Update it
    response = await test_client.put(
        f"/api/v1/controls/{control_id}",
        headers=superuser_token_headers,
        json={"name": "Updated Control Name"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Control Name"


@pytest.mark.anyio
async def test_delete_control(test_client: AsyncClient, superuser_token_headers):
    # Create a control
    create_response = await test_client.post(
        "/api/v1/controls",
        headers=superuser_token_headers,
        json={
            "name": "Test Control Delete",
            "description": "A test control for delete",
            "type": "Preventive",
        },
    )
    control_id = create_response.json()["id"]

    # Delete it
    response = await test_client.delete(
        f"/api/v1/controls/{control_id}", headers=superuser_token_headers
    )
    assert response.status_code == 204

    # Verify it's gone
    get_response = await test_client.get(
        f"/api/v1/controls/{control_id}", headers=superuser_token_headers
    )
    assert get_response.status_code == 404


# --- Risks Tests ---


@pytest.mark.anyio
async def test_create_risk(test_client: AsyncClient, superuser_token_headers):
    response = await test_client.post(
        "/api/v1/risks",
        headers=superuser_token_headers,
        json={
            "name": "Test Risk",
            "description": "A test risk",
            "category": "Financial",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Risk"
    assert "id" in data


@pytest.mark.anyio
async def test_read_risks(test_client: AsyncClient, superuser_token_headers):
    # Create a risk
    await test_client.post(
        "/api/v1/risks",
        headers=superuser_token_headers,
        json={
            "name": "Test Risk List",
            "description": "A test risk for list",
            "category": "Financial",
        },
    )

    response = await test_client.get("/api/v1/risks", headers=superuser_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) > 0


# --- Business Processes Tests ---


@pytest.mark.anyio
async def test_create_business_process(
    test_client: AsyncClient, superuser_token_headers
):
    response = await test_client.post(
        "/api/v1/business-processes",
        headers=superuser_token_headers,
        json={"name": "Test Process", "description": "A test process"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Process"
    assert "id" in data


# --- Regulatory Frameworks Tests ---


@pytest.mark.anyio
async def test_create_regulatory_framework(
    test_client: AsyncClient, superuser_token_headers
):
    response = await test_client.post(
        "/api/v1/regulatory-frameworks",
        headers=superuser_token_headers,
        json={
            "name": "Test Framework",
            "description": "A test framework",
            "version": "1.0",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Framework"
    assert "id" in data
