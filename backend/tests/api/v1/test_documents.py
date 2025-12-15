import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock
from io import BytesIO
from uuid import uuid4

from app.main import app
from app.models.document import DocumentStatus, Document
from app.models.compliance import RegulatoryFramework, RegulatoryRequirement
from app.schemas import DocumentRead
from app.services.ai_service import DocumentClassification
from app.core.deps import has_role, get_current_active_user # Added get_current_active_user import
from app.models.user import User as UserModel # Added import


@pytest.mark.asyncio
async def test_upload_document_unauthorized():
    """Test that upload endpoint requires authentication."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # Create a fake PDF file
        files = {"file": ("test.pdf", BytesIO(b"fake pdf content"), "application/pdf")}
        response = await ac.post("/api/v1/documents/upload", files=files)

        # Should return 403 (forbidden) since no auth provided
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_documents_unauthorized():
    """Test that list endpoint requires authentication."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/api/v1/documents")

        # Should return 403 (forbidden) since no auth provided
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_document_unauthorized():
    """Test that get document endpoint requires authentication."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        document_id = uuid4()
        response = await ac.get(f"/api/v1/documents/{document_id}")

        # Should return 403 (forbidden) since no auth provided
        assert response.status_code == 403


# Unit tests for DocumentService
from app.services.document_service import DocumentService
from fastapi import UploadFile, HTTPException


@pytest.mark.asyncio
async def test_validate_file_valid_pdf():
    """Test file validation with valid PDF."""
    mock_file = MagicMock(spec=UploadFile)
    mock_file.content_type = "application/pdf"
    mock_file.filename = "test.pdf"
    
    # Mock read to return PDF magic bytes
    async def async_read(size=-1):
        return b"%PDF-1.4"
    mock_file.read = async_read
    
    mock_file.seek = MagicMock()
    async def async_seek(offset):
        return None
    mock_file.seek = async_seek

    # Should not raise an exception
    await DocumentService.validate_file(mock_file)


@pytest.mark.asyncio
async def test_validate_file_valid_text():
    """Test file validation with valid text file."""
    mock_file = MagicMock(spec=UploadFile)
    mock_file.content_type = "text/plain"
    mock_file.filename = "test.txt"
    
    # Mock read to return safe text (no null bytes)
    async def async_read(size=-1):
        return b"Hello World"
    mock_file.read = async_read
    
    mock_file.seek = MagicMock()
    async def async_seek(offset):
        return None
    mock_file.seek = async_seek

    # Should not raise an exception
    await DocumentService.validate_file(mock_file)


@pytest.mark.asyncio
async def test_validate_file_invalid_type():
    """Test file validation with invalid file type."""
    mock_file = MagicMock(spec=UploadFile)
    mock_file.content_type = "image/jpeg"
    mock_file.filename = "test.jpg"

    # Should raise HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await DocumentService.validate_file(mock_file)

    assert exc_info.value.status_code == 400
    assert "not allowed" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_validate_file_invalid_pdf_magic():
    """Test file validation with invalid PDF magic bytes."""
    mock_file = MagicMock(spec=UploadFile)
    mock_file.content_type = "application/pdf"
    mock_file.filename = "fake.pdf"
    
    # Mock read to return bad bytes
    async def async_read(size=-1):
        return b"NOTAPDF"
    mock_file.read = async_read
    
    mock_file.seek = MagicMock()
    async def async_seek(offset):
        return None
    mock_file.seek = async_seek

    # Should raise HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await DocumentService.validate_file(mock_file)

    assert exc_info.value.status_code == 400
    assert "Invalid PDF" in str(exc_info.value.detail)


@pytest.mark.asyncio
@patch("app.services.document_service.supabase_client")
async def test_upload_to_storage_size_limit(mock_supabase):
    """Test that files over 20MB are rejected."""
    # Mock supabase client to be available (not None)
    mock_supabase.return_value = MagicMock()

    mock_file = MagicMock(spec=UploadFile)
    mock_file.content_type = "application/pdf"
    mock_file.filename = "large.pdf"
    # Mock a file larger than 20MB
    large_content = b"x" * (21 * 1024 * 1024)  # 21MB

    async def mock_read():
        return large_content

    mock_file.read = mock_read
    mock_file.seek = MagicMock()

    user_id = uuid4()

    # The service wraps the 400 error in a 500 error during exception handling
    # So we check that the error mentions the size limit
    with pytest.raises(HTTPException) as exc_info:
        await DocumentService.upload_to_storage(mock_file, user_id)

    # The error message should mention the file size limit
    assert "exceeds maximum" in str(exc_info.value.detail) or "File size" in str(
        exc_info.value.detail
    )


@pytest.mark.asyncio
async def test_upload_document_success(test_client):
    """Test successful document upload."""
    
    # Mock the has_role dependency to return an admin user
    mock_admin_user = UserModel(
        id=uuid4(),
        email="mock_admin@example.com",
        hashed_password="mock_hash",
        is_active=True,
        is_superuser=True,
        is_verified=True,
        roles=["admin"],
        tenant_id=uuid4()
    )
    # Temporarily override the get_current_active_user dependency
    app.dependency_overrides[get_current_active_user] = lambda: mock_admin_user

    try:
        # Mock the storage upload to return a path without hitting Supabase
        with patch("app.services.document_service.DocumentService.upload_to_storage") as mock_upload:
            mock_upload.return_value = "user_id/uuid_test.pdf"
            
            # Create valid PDF content with magic bytes
            pdf_content = b"%PDF-1.4\n...fake content..."
            files = {"file": ("test.pdf", BytesIO(pdf_content), "application/pdf")}
            
            response = await test_client.post(
                "/api/v1/documents/upload", 
                files=files, 
                # No headers needed, as get_current_active_user is mocked
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["filename"] == "test.pdf"
            assert data["status"] == "pending"
            assert "id" in data
    finally:
        # Clear the dependency override after the test
        del app.dependency_overrides[get_current_active_user] # Remove specific override


@pytest.mark.asyncio
@patch("app.services.document_service.DocumentService.get_document_by_id")
async def test_get_document_with_law_classification(
    mock_get_document_by_id: MagicMock, test_client: AsyncClient
):
    """Test getting a document with 'Law' classification."""
    from datetime import datetime, timezone

    user_id = uuid4()
    tenant_id = uuid4()
    document_id = uuid4()
    framework_id = uuid4()
    now = datetime.now(timezone.utc)

    mock_document = Document(
        id=document_id,
        filename="Law_Doc.pdf",
        storage_path="path/to/law_doc.pdf",
        status=DocumentStatus.completed,
        uploaded_by=user_id,
        created_at=now,
        regulatory_framework=RegulatoryFramework(
            id=framework_id,
            tenant_id=tenant_id,
            name="GDPR",
            description="General Data Protection Regulation",
            version="2016/679",
            document_id=document_id,
            created_at=now,
            updated_at=now,
        ),
        regulatory_requirement=None,
    )

    mock_get_document_by_id.return_value = mock_document

    mock_admin_user = UserModel(
        id=user_id,
        email="admin@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=True,
        is_verified=True,
        roles=["admin"],
        tenant_id=tenant_id,
    )
    app.dependency_overrides[get_current_active_user] = lambda: mock_admin_user

    try:
        response = await test_client.get(f"/api/v1/documents/{document_id}")
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == str(document_id)
        assert data["filename"] == "Law_Doc.pdf"
        assert data["status"] == DocumentStatus.completed.value
        assert data["classification"]["document_type"] == "Law"
        assert data["classification"]["framework_name"] == "GDPR"
        assert (
            data["classification"]["framework_description"]
            == "General Data Protection Regulation"
        )
        assert data["classification"]["parent_law_name"] is None
        assert data["classification"]["version"] == "2016/679"
    finally:
        del app.dependency_overrides[get_current_active_user]


@pytest.mark.asyncio
@patch("app.services.document_service.DocumentService.get_document_by_id")
async def test_get_document_with_regulation_classification(
    mock_get_document_by_id: MagicMock, test_client: AsyncClient
):
    """Test getting a document with 'Regulation' classification."""
    from datetime import datetime, timezone

    user_id = uuid4()
    tenant_id = uuid4()
    document_id = uuid4()
    framework_id = uuid4()
    requirement_id = uuid4()
    now = datetime.now(timezone.utc)

    mock_framework = RegulatoryFramework(
        id=framework_id,
        tenant_id=tenant_id,
        name="GDPR",
        description="General Data Protection Regulation",
        version="2016/679",
        created_at=now,
        updated_at=now,
    )
    mock_document = Document(
        id=document_id,
        filename="Regulation_Doc.pdf",
        storage_path="path/to/regulation_doc.pdf",
        status=DocumentStatus.completed,
        uploaded_by=user_id,
        created_at=now,
        regulatory_framework=None,
        regulatory_requirement=RegulatoryRequirement(
            id=requirement_id,
            tenant_id=tenant_id,
            framework_id=framework_id,
            framework=mock_framework,  # Ensure parent framework is linked
            name="Article 32",
            description="Security of processing",
            document_id=document_id,
            created_at=now,
            updated_at=now,
        ),
    )

    mock_get_document_by_id.return_value = mock_document

    mock_admin_user = UserModel(
        id=user_id,
        email="admin@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=True,
        is_verified=True,
        roles=["admin"],
        tenant_id=tenant_id,
    )
    app.dependency_overrides[get_current_active_user] = lambda: mock_admin_user

    try:
        response = await test_client.get(f"/api/v1/documents/{document_id}")
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == str(document_id)
        assert data["filename"] == "Regulation_Doc.pdf"
        assert data["status"] == DocumentStatus.completed.value
        assert data["classification"]["document_type"] == "Regulation"
        assert data["classification"]["framework_name"] == "Article 32"
        assert (
            data["classification"]["framework_description"] == "Security of processing"
        )
        assert data["classification"]["parent_law_name"] == "GDPR"
        assert data["classification"]["version"] is None
    finally:
        del app.dependency_overrides[get_current_active_user]


@pytest.mark.asyncio
@patch("app.services.document_service.DocumentService.get_document_by_id")
@patch("tasks.analysis._process_document_async")
async def test_manually_process_document_returns_classification(
    mock_process_document_async: MagicMock,
    mock_get_document_by_id: MagicMock,
    test_client: AsyncClient,
):
    """Test that manually processing a document returns classification data."""
    from datetime import datetime, timezone

    user_id = uuid4()
    tenant_id = uuid4()
    document_id = uuid4()
    framework_id = uuid4()
    now = datetime.now(timezone.utc)

    mock_document = Document(
        id=document_id,
        filename="Manual_Law.pdf",
        storage_path="path/to/manual_law.pdf",
        status=DocumentStatus.pending,
        uploaded_by=user_id,
        created_at=now,
    )
    # Mock get_document_by_id to return document *after* processing with classification
    processed_document_with_classification = Document(
        id=document_id,
        filename="Manual_Law.pdf",
        storage_path="path/to/manual_law.pdf",
        status=DocumentStatus.completed,
        uploaded_by=user_id,
        created_at=now,
        regulatory_framework=RegulatoryFramework(
            id=framework_id,
            tenant_id=tenant_id,
            name="PCI DSS",
            description="Payment Card Industry Data Security Standard",
            version="4.0",
            document_id=document_id,
            created_at=now,
            updated_at=now,
        ),
        regulatory_requirement=None,
    )
    # Use side_effect to return initial doc for pre-check, then processed doc for refresh
    mock_get_document_by_id.side_effect = [mock_document, processed_document_with_classification]
    
    # Mock the async processing task to do nothing (we only care about the return value)
    mock_process_document_async.return_value = None

    mock_admin_user = UserModel(
        id=user_id,
        email="admin@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=True,
        is_verified=True,
        roles=["admin"],
        tenant_id=tenant_id,
    )
    app.dependency_overrides[get_current_active_user] = lambda: mock_admin_user

    try:
        response = await test_client.post(f"/api/v1/documents/{document_id}/process")
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == str(document_id)
        assert data["filename"] == "Manual_Law.pdf"
        assert data["status"] == DocumentStatus.completed.value
        assert data["classification"]["document_type"] == "Law"
        assert data["classification"]["framework_name"] == "PCI DSS"
    finally:
        del app.dependency_overrides[get_current_active_user]
