import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import HTTPException, UploadFile, status
from app.services.document_service import DocumentService
import uuid

@pytest.mark.asyncio
async def test_upload_to_storage_too_large():
    # Mock UploadFile
    file_mock = MagicMock(spec=UploadFile)
    file_mock.filename = "large_file.pdf"
    file_mock.content_type = "application/pdf"
    
    # Mock read to return content larger than MAX_FILE_SIZE (20MB)
    # 20MB + 1 byte
    large_content = b"a" * (20 * 1024 * 1024 + 1)
    file_mock.read = AsyncMock(return_value=large_content)
    file_mock.seek = AsyncMock()

    # Mock supabase_client (should exist to pass the initial check)
    with patch("app.services.document_service.supabase_client") as mock_supabase:
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await DocumentService.upload_to_storage(file_mock, user_id=uuid.uuid4())
        
        # Assert it's 413, not 500 (and definitely not 400)
        assert exc_info.value.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        assert "exceeds maximum" in exc_info.value.detail

@pytest.mark.asyncio
async def test_upload_to_storage_valid_size():
    # Mock UploadFile
    file_mock = MagicMock(spec=UploadFile)
    file_mock.filename = "valid_file.pdf"
    file_mock.content_type = "application/pdf"
    
    # Valid content
    valid_content = b"valid content"
    file_mock.read = AsyncMock(return_value=valid_content)
    file_mock.seek = AsyncMock()

    with patch("app.services.document_service.supabase_client") as mock_supabase:
        # Mock upload response
        mock_supabase.storage.from_.return_value.upload.return_value = {"key": "some/path"}
        
        # Act
        result = await DocumentService.upload_to_storage(file_mock, user_id=uuid.uuid4())
        
        # Assert
        assert result is not None
        assert "production/" in result
