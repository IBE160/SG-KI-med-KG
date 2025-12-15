from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import logging
import uuid
from sqlalchemy.future import select

from app.core.celery_app import celery_app

# Internal imports need to be careful with Celery context
from app.database import async_session_maker
from app.models.document import Document, DocumentStatus
from app.models.suggestion import AISuggestion, SuggestionStatus
from app.models.compliance import RegulatoryFramework, RegulatoryRequirement
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
            logger.info(f"[STEP 1/6] Fetching document {document_id}")
            # 1. Fetch Document
            document = await db.get(Document, document_id)
            if not document:
                logger.error(f"Document {document_id} not found in database")
                return

            logger.info(f"[STEP 1/6] ✓ Document found: {document.filename}")

            # Fetch uploader to get tenant_id for suggestions
            from app.models.user import User
            uploader = await db.get(User, document.uploaded_by)
            tenant_id = uploader.tenant_id if uploader else None
            if not tenant_id:
                logger.warning(f"Document {document_id} uploader has no tenant_id")

            # Update status to processing
            document.status = DocumentStatus.processing
            await db.commit()
            logger.info(f"[STEP 2/6] ✓ Status updated to processing")

            # 2. Download File
            logger.info(f"[STEP 2/6] Downloading file from Supabase: {document.storage_path}")
            client = get_supabase_client()
            if not client:
                raise ValueError("Supabase client not initialized")

            # Download file content
            file_bytes = client.storage.from_(DocumentService.BUCKET_NAME).download(document.storage_path)
            logger.info(f"[STEP 2/6] ✓ Downloaded {len(file_bytes)} bytes")

            # 3. Extract Text
            logger.info(f"[STEP 3/6] Extracting text from {document.filename}")
            text_content = ""
            if document.filename.lower().endswith(".pdf"):
                from pypdf import PdfReader
                from io import BytesIO

                try:
                    reader = PdfReader(BytesIO(file_bytes))
                    logger.info(f"[STEP 3/6] PDF has {len(reader.pages)} pages")
                    for i, page in enumerate(reader.pages):
                        page_text = page.extract_text()
                        text_content += page_text + "\n"
                        logger.info(f"[STEP 3/6] Page {i+1}: extracted {len(page_text)} chars")
                except Exception as e:
                    logger.error(f"[STEP 3/6] ✗ PDF extraction failed: {e}")
                    raise ValueError(f"Failed to extract text from PDF: {e}")
            else:
                # Assume text/plain
                text_content = file_bytes.decode("utf-8", errors="ignore")
                logger.info(f"[STEP 3/6] Text file decoded: {len(text_content)} chars")

            if not text_content.strip():
                logger.error(f"[STEP 3/6] ✗ Extracted text is empty")
                raise ValueError("Extracted text is empty")

            logger.info(f"[STEP 3/6] ✓ Extracted {len(text_content)} characters")

            # 4. AI Analysis
            logger.info(f"[STEP 4/6] Calling AI service for analysis")
            ai_service = AIService()
            analysis_result = await ai_service.analyze_document(text_content)
            logger.info(f"[STEP 4/6] ✓ AI returned {len(analysis_result.suggestions)} suggestions")

            # 4.5 Process Classification
            if analysis_result.classification:
                logger.info(f"[STEP 4.5/6] Processing classification: {analysis_result.classification.document_type}")
                cls = analysis_result.classification
                
                if cls.document_type == "Law":
                    # Check if framework exists
                    stmt = select(RegulatoryFramework).filter(
                        RegulatoryFramework.tenant_id == tenant_id,
                        RegulatoryFramework.name == cls.framework_name
                    )
                    result = await db.execute(stmt)
                    framework = result.scalars().first()
                    
                    if not framework:
                        framework = RegulatoryFramework(
                            tenant_id=tenant_id,
                            name=cls.framework_name,
                            description=cls.framework_description,
                            version=cls.version,
                            document_id=document.id
                        )
                        db.add(framework)
                        logger.info(f"[STEP 4.5/6] Created new Framework: {cls.framework_name}")
                    else:
                        framework.description = cls.framework_description or framework.description
                        framework.version = cls.version or framework.version
                        framework.document_id = document.id
                        logger.info(f"[STEP 4.5/6] Updated Framework: {cls.framework_name}")
                        
                elif cls.document_type == "Regulation":
                    # 1. Ensure parent framework exists
                    parent_name = cls.parent_law_name or "Unknown Law"
                    stmt = select(RegulatoryFramework).filter(
                        RegulatoryFramework.tenant_id == tenant_id,
                        RegulatoryFramework.name == parent_name
                    )
                    result = await db.execute(stmt)
                    parent_framework = result.scalars().first()
                    
                    if not parent_framework:
                        parent_framework = RegulatoryFramework(
                            tenant_id=tenant_id,
                            name=parent_name,
                            description=f"Auto-created parent for {cls.framework_name}",
                            version=cls.version
                        )
                        db.add(parent_framework)
                        await db.flush() # Need ID
                        logger.info(f"[STEP 4.5/6] Auto-created parent Framework: {parent_name}")
                    
                    # 2. Check/Create Requirement
                    stmt = select(RegulatoryRequirement).filter(
                        RegulatoryRequirement.tenant_id == tenant_id,
                        RegulatoryRequirement.framework_id == parent_framework.id,
                        RegulatoryRequirement.name == cls.framework_name
                    )
                    result = await db.execute(stmt)
                    requirement = result.scalars().first()
                    
                    if not requirement:
                        requirement = RegulatoryRequirement(
                            tenant_id=tenant_id,
                            framework_id=parent_framework.id,
                            name=cls.framework_name,
                            description=cls.framework_description,
                            document_id=document.id
                        )
                        db.add(requirement)
                        logger.info(f"[STEP 4.5/6] Created new Requirement: {cls.framework_name}")
                    else:
                        requirement.description = cls.framework_description or requirement.description
                        requirement.document_id = document.id
                        logger.info(f"[STEP 4.5/6] Updated Requirement: {cls.framework_name}")
            else:
                 logger.warning("[STEP 4.5/6] No classification returned from AI")

            # 5. Save Suggestions
            logger.info(f"[STEP 5/6] Saving {len(analysis_result.suggestions)} suggestions to database")
            for i, item in enumerate(analysis_result.suggestions):
                suggestion = AISuggestion(
                    document_id=document.id,
                    tenant_id=tenant_id,
                    type=item.type,
                    content=item.content,
                    rationale=item.rationale,
                    source_reference=item.source_reference,
                    status=SuggestionStatus.pending
                )
                db.add(suggestion)
                logger.info(f"[STEP 5/6] Suggestion {i+1}: type={item.type}, status=pending")

            # 6. Complete
            logger.info(f"[STEP 6/6] Committing changes and marking document as completed")
            document.status = DocumentStatus.completed
            await db.commit()
            logger.info(f"[STEP 6/6] ✓ Document {document_id} analysis completed successfully")

        except Exception as e:
            logger.exception(f"✗ Error processing document {document_id}: {e}")
            # Update status to failed
            try:
                # Re-fetch in case session was rolled back
                document = await db.get(Document, document_id)
                if document:
                    document.status = DocumentStatus.failed
                    await db.commit()
                    logger.error(f"Document {document_id} marked as FAILED")
            except Exception as db_e:
                logger.error(f"Failed to update document status to failed: {db_e}")

@celery_app.task(name="process_document")
def process_document(document_id_str: str):
    """
    Celery task entry point.
    """
    print(f"DEBUG: Celery Task process_document START for {document_id_str}")
    try:
        # Celery doesn't natively support async/await tasks in standard pool
        # We use asyncio.run to execute the async logic
        document_id = uuid.UUID(document_id_str)
        asyncio.run(_process_document_async(document_id))
        print(f"DEBUG: Celery Task process_document FINISHED logic")
    except Exception as e:
        print(f"CRITICAL ERROR IN TASK: {e}")
        import traceback
        traceback.print_exc()
    print(f"DEBUG: Celery Task process_document END")
