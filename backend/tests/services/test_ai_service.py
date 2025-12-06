import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.ai_service import AIService, AnalysisResult, Suggestion
from app.config import settings
import json

@pytest.mark.asyncio
async def test_analyze_document_success():
    """Test that analyze_document parses valid JSON response."""
    mock_response_content = json.dumps({
        "suggestions": [
            {
                "type": "risk",
                "content": {"description": "Risk 1", "severity": "high"},
                "rationale": "Because...",
                "source_reference": "Section 1"
            }
        ]
    })

    # Mock the client and its completion method
    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content=mock_response_content))]
    
    # Async mock for the create method
    mock_create = AsyncMock(return_value=mock_completion)
    mock_client.chat.completions.create = mock_create

    # Inject the mock client
    service = AIService(client=mock_client)
    result = await service.analyze_document("Test text")

    assert isinstance(result, AnalysisResult)
    assert len(result.suggestions) == 1
    assert result.suggestions[0].type == "risk"
    assert result.suggestions[0].rationale == "Because..."

@pytest.mark.asyncio
async def test_analyze_document_empty_response():
    """Test handling of empty AI response."""
    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content=""))]
    
    mock_create = AsyncMock(return_value=mock_completion)
    mock_client.chat.completions.create = mock_create

    service = AIService(client=mock_client)
    result = await service.analyze_document("Test text")
    assert isinstance(result, AnalysisResult)
    assert len(result.suggestions) == 0

@pytest.mark.asyncio
async def test_analyze_document_missing_key():
    """Test error when API key is missing and no client provided."""
    with patch.object(settings, 'OPENAI_API_KEY', None):
        service = AIService()
        with pytest.raises(ValueError, match="OPENAI_API_KEY is not set"):
            await service.analyze_document("Test text")
