import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import uuid
from app.models.document import Document, DocumentStatus
from app.models.suggestion import AISuggestion
from tasks.analysis import _process_document_async

@pytest.mark.asyncio
async def test_process_document_success():
    """Test full document processing pipeline (mocked)."""
    document_id = uuid.uuid4()
    mock_document = Document(
        id=document_id,
        filename="test.pdf",
        storage_path="path/to/test.pdf",
        status=DocumentStatus.pending,
        uploaded_by=uuid.uuid4() # Add missing field
    )
    
    # Mock DB session
    mock_db = AsyncMock()
    mock_db.get.return_value = mock_document
    
    # Mock async_session_maker context manager
    mock_session_maker = MagicMock()
    mock_session_maker.__aenter__.return_value = mock_db
    mock_session_maker.__aexit__.return_value = None

    # Mock Supabase Client
    mock_storage = MagicMock()
    mock_storage.download.return_value = b"%PDF-1.4 content" # Valid PDF header
    
    mock_supabase = MagicMock()
    mock_supabase.storage.from_.return_value = mock_storage
    
    # Mock PDF Reader
    mock_reader = MagicMock()
    page = MagicMock()
    page.extract_text.return_value = "Extracted PDF Content"
    mock_reader.pages = [page]
    
    # Mock AI Service
    mock_analysis_result = MagicMock()
    mock_suggestion = MagicMock()
    mock_suggestion.type = "risk"
    mock_suggestion.content = {"desc": "test"}
    mock_suggestion.rationale = "because"
    mock_suggestion.source_reference = "ref"
    mock_analysis_result.suggestions = [mock_suggestion]
    
    mock_ai_service = AsyncMock()
    mock_ai_service.analyze_document.return_value = mock_analysis_result

    with patch("tasks.analysis.async_session_maker", return_value=mock_session_maker), \
         patch("tasks.analysis.get_supabase_client", return_value=mock_supabase), \
         patch("tasks.analysis.AIService", return_value=mock_ai_service), \
         patch("pypdf.PdfReader", return_value=mock_reader):
         
        await _process_document_async(document_id)
        
        # Verify Status Updates
        assert mock_document.status == DocumentStatus.completed
        
        # Verify AI Service called
        mock_ai_service.analyze_document.assert_called_once()
        
        # Verify Suggestion Added
        mock_db.add.assert_called()
        # Inspect the added object to ensure it is an AISuggestion
        args, _ = mock_db.add.call_args
        assert isinstance(args[0], AISuggestion)

@pytest.mark.asyncio
async def test_process_document_failure():
    """Test failure handling in document processing."""
    document_id = uuid.uuid4()
    mock_document = Document(
        id=document_id, 
        filename="test.txt", 
        storage_path="path", 
        status=DocumentStatus.pending,
        uploaded_by=uuid.uuid4() # Add missing field
    )
    
    mock_db = AsyncMock()
    mock_db.get.return_value = mock_document
    
    mock_session_maker = MagicMock()
    mock_session_maker.__aenter__.return_value = mock_db
    mock_session_maker.__aexit__.return_value = None

    # Force an error during download
    with patch("tasks.analysis.async_session_maker", return_value=mock_session_maker), \
         patch("tasks.analysis.get_supabase_client", side_effect=Exception("Storage Down")):
         
        await _process_document_async(document_id)
        
        # Verify status update to failed
        assert mock_document.status == DocumentStatus.failed
