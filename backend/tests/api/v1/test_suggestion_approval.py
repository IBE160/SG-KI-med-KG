import pytest
from uuid import uuid4
from httpx import AsyncClient, ASGITransport
from sqlalchemy.future import select
from app.main import app
from app.models.document import Document
from app.models.suggestion import AISuggestion, SuggestionStatus, SuggestionType
from app.models.compliance import Control

@pytest.mark.asyncio
async def test_approve_suggestion_creates_control_with_owner(
    db_session,
    test_client,
    bpo_user,
    bpo_token_headers
):
    """
    Reproduction test for Story 4-5:
    Verifies that approving a suggestion creates a Control with the correct owner_id (assigned BPO or approver).
    """
    # 1. Setup: Create a Document
    document = Document(
        id=uuid4(),
        filename="test.pdf",
        uploaded_by=bpo_user.id,
        storage_path="test/path"
    )
    db_session.add(document)
    await db_session.flush()

    # 2. Setup: Create a Suggestion (Control)
    suggestion_id = uuid4()
    suggestion = AISuggestion(
        id=suggestion_id,
        tenant_id=bpo_user.tenant_id,
        document_id=document.id,
        type=SuggestionType.control,
        content={"name": "Whistleblower Policy", "description": "Ensure whistleblowers are protected."},
        rationale="Important for compliance",
        source_reference="Page 1",
        status=SuggestionStatus.pending_review,
        assigned_bpo_id=bpo_user.id
    )
    db_session.add(suggestion)
    await db_session.commit()

    # 3. Action: Approve the suggestion via API
    approve_payload = {
        "name": "Whistleblower Policy Control",
        "description": "Active control for whistleblower protection."
    }
    
    response = await test_client.post(
        f"/api/v1/suggestions/{suggestion_id}/approve",
        headers=bpo_token_headers,
        json=approve_payload
    )
    
    # 4. Verification: Check Response
    assert response.status_code == 200, f"Approval failed: {response.text}"
    data = response.json()
    assert data["status"] == "active"

    # 5. Verification: Check Database for Control and owner_id
    result = await db_session.execute(
        select(Control).where(Control.name == "Whistleblower Policy Control")
    )
    control = result.scalar_one_or_none()
    
    assert control is not None, "Control was not created in the database"
    assert control.tenant_id == bpo_user.tenant_id, "Tenant ID mismatch"
    
    # THIS IS THE DEFECT: We expect this to FAIL currently because owner_id is missing
    assert control.owner_id == bpo_user.id, f"Control owner_id {control.owner_id} should be {bpo_user.id}"
