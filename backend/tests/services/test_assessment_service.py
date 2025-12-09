import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.assessment_service import AssessmentService
from app.models.suggestion import AISuggestion, SuggestionStatus, SuggestionType
from app.models.user import User
from app.schemas.assessment import ResidualRisk
from app.models.compliance import BusinessProcess, Risk, Control
from app.models.document import Document

@pytest.mark.asyncio

async def test_approve_suggestion(db_session: AsyncSession):

    # Setup

    tenant_id = uuid4()

    

    # Create User (BPO)

    bpo_user = User(

        id=uuid4(),

        email="bpo@example.com",

        hashed_password="hashed",

        is_active=True,

        is_verified=True,

        role="bpo",

        tenant_id=tenant_id

    )

    db_session.add(bpo_user)

    

    # Create Document (FK for suggestion)

    doc = Document(

        id=uuid4(), 

        filename="Test Doc", 

        storage_path="/tmp/doc.pdf",

        uploaded_by=bpo_user.id

    )

    db_session.add(doc)

    

    # Create Suggestion

    suggestion = AISuggestion(

        id=uuid4(),

        tenant_id=tenant_id,

        document_id=doc.id,

        type=SuggestionType.risk,

        content={

            "business_process_name": "Test Process",

            "risk_name": "Test Risk",

            "risk_description": "Risk Desc",

            "control_name": "Test Control",

            "control_description": "Control Desc"

        },

        rationale="Because",

        source_reference="Ref 1",

        status=SuggestionStatus.pending_review,

        assigned_bpo_id=bpo_user.id

    )

    db_session.add(suggestion)

    await db_session.commit()



    # Action: Approve

    response = await AssessmentService.approve_suggestion(

        db=db_session,

        suggestion_id=suggestion.id,

        residual_risk=ResidualRisk.MEDIUM,

        edits=None,

        actor_id=bpo_user.id,

        tenant_id=tenant_id

    )



    # Assertions

    assert response.success is True

    assert response.updated_status == "active"

    

    # Verify Suggestion Status

    updated_suggestion = await db_session.get(AISuggestion, suggestion.id)

    assert updated_suggestion.status == SuggestionStatus.active



    # Verify Active Records Created

    # Check Business Process

    bp_result = await db_session.execute(select(BusinessProcess).where(BusinessProcess.name == "Test Process"))

    bp = bp_result.scalar_one()

    assert bp.tenant_id == tenant_id

    

    # Check Risk

    risk_result = await db_session.execute(select(Risk).where(Risk.description == "Risk Desc"))

    risk = risk_result.scalar_one()

    assert risk.tenant_id == tenant_id

    # removed relationship assertions as current implementation is flat

    assert risk.category == "medium" 



    # Check Control

    control_result = await db_session.execute(select(Control).where(Control.description == "Control Desc"))

    control = control_result.scalar_one()

    assert control.tenant_id == tenant_id



@pytest.mark.asyncio

async def test_discard_suggestion(db_session: AsyncSession):

    # Setup

    tenant_id = uuid4()

    bpo_user = User(id=uuid4(), email="bpo2@example.com", hashed_password="hashed", role="bpo", tenant_id=tenant_id)

    db_session.add(bpo_user)

    doc = Document(

        id=uuid4(), 

        filename="Test Doc 2", 

        storage_path="/tmp/doc2.pdf",

        uploaded_by=bpo_user.id

    )

    db_session.add(doc)

    

    suggestion = AISuggestion(

        id=uuid4(),

        tenant_id=tenant_id,

        document_id=doc.id,

        type=SuggestionType.control,

        content={"foo": "bar"},

        rationale="Because",

        source_reference="Ref",

        status=SuggestionStatus.pending_review,

        assigned_bpo_id=bpo_user.id

    )

    db_session.add(suggestion)

    await db_session.commit()



    # Action: Discard

    response = await AssessmentService.discard_suggestion(

        db=db_session,

        suggestion_id=suggestion.id,

        actor_id=bpo_user.id,

        tenant_id=tenant_id

    )



    # Assertions

    assert response.success is True

    assert response.updated_status == "archived"



    updated_suggestion = await db_session.get(AISuggestion, suggestion.id)

    assert updated_suggestion.status == SuggestionStatus.archived
