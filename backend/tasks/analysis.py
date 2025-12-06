import uuid
from celery import shared_task
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import logging

# Internal imports need to be careful with Celery context
from app.database import async_session_maker
from app.models.document import Document, DocumentStatus
from app.models.suggestion import AISuggestion, SuggestionStatus
from app.services.document_service import DocumentService
from app.services.ai_service import AIService
from app.core.supabase import supabase_client, get_supabase_client # Ensure we have access

logger = logging.getLogger(__name__)

async def _process_document_async(document_id: uuid.UUID):
    """
    Async worker function to handle the logic.
    Celery tasks are synchronous by default, so we bridge here.
    """
    async with async_session_maker() as db:
        try:
            # 1. Fetch Document
            document = await db.get(Document, document_id)
            if not document:
                logger.error(f"Document {document_id} not found.")
                return

            # Update status to processing
            document.status = DocumentStatus.processing
            await db.commit()

            # 2. Download File
            # Using the supabase client directly or via a helper
            client = get_supabase_client()
            if not client:
                 raise ValueError("Supabase client not initialized")

            # Download file content
            # Supabase-py storage download returns bytes
            file_bytes = client.storage.from_(DocumentService.BUCKET_NAME).download(document.storage_path)
            
            # 3. Extract Text
            text_content = ""
            if document.filename.lower().endswith(".pdf"):
                from pypdf import PdfReader
                from io import BytesIO
                
                try:
                    reader = PdfReader(BytesIO(file_bytes))
                    for page in reader.pages:
                        text_content += page.extract_text() + "\n"
                except Exception as e:
                    logger.error(f"PDF extraction failed: {e}")
                    raise ValueError("Failed to extract text from PDF")
            else:
                # Assume text/plain
                text_content = file_bytes.decode("utf-8", errors="ignore")

            if not text_content.strip():
                raise ValueError("Extracted text is empty")

            # 4. AI Analysis
            ai_service = AIService()
            analysis_result = await ai_service.analyze_document(text_content)

            # 5. Save Suggestions
            for item in analysis_result.suggestions:
                suggestion = AISuggestion(
                    document_id=document.id,
                    type=item.type,
                    content=item.content,
                    rationale=item.rationale,
                    source_reference=item.source_reference,
                    status=SuggestionStatus.pending
                )
                db.add(suggestion)

            # 6. Complete
            document.status = DocumentStatus.completed
            await db.commit()
            logger.info(f"Document {document_id} analysis completed successfully.")

        except Exception as e:
            logger.exception(f"Error processing document {document_id}: {e}")
            # Update status to failed
            try:
                # Re-fetch in case session was rolled back
                document = await db.get(Document, document_id)
                if document:
                    document.status = DocumentStatus.failed
                    await db.commit()
            except Exception as db_e:
                logger.error(f"Failed to update document status to failed: {db_e}")

@shared_task(name="process_document")
def process_document(document_id_str: str):
    """
    Celery task entry point.
    Args:
        document_id_str: UUID string of the document.
    """
    # Celery doesn't natively support async/await tasks in standard pool
    # We use asyncio.run to execute the async logic
    document_id = uuid.UUID(document_id_str)
    asyncio.run(_process_document_async(document_id))
