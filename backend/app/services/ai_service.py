import os
import uuid
from typing import List, Dict, Any
from pydantic import BaseModel, Field
import openai
from app.config import settings
from app.schemas.suggestion import AISuggestionCreate, SuggestionType, SuggestionStatus

# --- Schema Definitions ---
# Define Pydantic models that structure the expected LLM output.
# This will be used for JSON mode or Function Calling validation.

class Suggestion(BaseModel):
    type: SuggestionType = Field(..., description="Type of the suggestion: 'risk' or 'control'.")
    content: Dict[str, Any] = Field(..., description="Key-value pairs describing the risk or control.")
    rationale: str = Field(..., description="Reasoning for why this is a risk or control.")
    source_reference: str = Field(..., description="Verbatim reference or clear pointer to the source text (e.g., 'Section 4.2').")

class AnalysisResult(BaseModel):
    suggestions: List[Suggestion] = Field(..., description="List of identified risks and controls.")

class AIService:
    """Service for analyzing documents using OpenAI LLM."""

    SYSTEM_PROMPT = """
You are an expert AI Legal Specialist in Risk and Compliance.
Your task is to analyze the provided regulatory document text and identify potential Risks and Controls.

For each identified item, return a JSON object with the following structure:
{
  "suggestions": [
    {
      "type": "risk" or "control",
      "content": {
        "description": "Brief description of the risk or control",
        "severity": "Low|Medium|High" (for risks only),
        "impact": "Potential impact description" (for risks only),
        "control_type": "Preventive|Detective|Corrective" (for controls only)
      },
      "rationale": "Clear explanation of why this is a risk or control and its significance",
      "source_reference": "Specific citation from the document (e.g., 'Section 4.2', 'Page 5, Paragraph 3')"
    }
  ]
}

IMPORTANT:
- "type" must be EXACTLY "risk" or "control" (lowercase, no other values)
- "content" must be a JSON object (not flat fields)
- "rationale" is a separate field explaining WHY this matters
- "source_reference" should cite the exact location in the document

Output MUST be valid JSON matching this exact structure.
    """

    def __init__(self, client: openai.AsyncOpenAI = None):
        # Configure OpenAI client
        # Assuming OPENAI_API_KEY is set in settings
        if client:
            self.client = client
        elif settings.OPENAI_API_KEY:
            self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None

    async def analyze_document(self, text: str) -> AnalysisResult:
        """
        Analyzes the provided text using GPT-4 to identify risks and controls.
        
        Args:
            text: The extracted text from the document.
            
        Returns:
            AnalysisResult: Structured list of suggestions.
        """
        if not self.client and not settings.OPENAI_API_KEY:
             # For development/testing without a key, we might want to return a dummy response
             # or raise an error. Raising error is safer for production.
             raise ValueError("OPENAI_API_KEY is not set.")
        
        if not self.client:
             self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        # Chunking logic (simplified for MVP)
        # A real implementation would need robust token counting and chunking.
        # For now, we'll truncate if too long, but standard GPT-4o-mini has 128k context, 
        # which covers most regulatory docs.
        # Let's assume the text fits for MVP.
        
        try:
            completion = await self.client.chat.completions.create(
                model="gpt-4o-mini", # Use a cost-effective but capable model
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": f"Analyze the following text:\n\n{text}"}
                ],
                response_format={"type": "json_object"}, # Force JSON output
                temperature=0.0 # Deterministic output
            )

            content = completion.choices[0].message.content
            if not content:
                return AnalysisResult(suggestions=[])

            # Log raw AI response for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"[AI RESPONSE RAW] {content[:500]}...")

            # Parse and validate with Pydantic
            # Using model_validate_json is cleaner than json.loads
            return AnalysisResult.model_validate_json(content)

        except Exception as e:
            # Log the error
            print(f"AI Analysis failed: {e}")
            # Re-raise or return empty depending on desired resilience
            raise e
