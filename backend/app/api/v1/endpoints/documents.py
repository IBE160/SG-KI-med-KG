from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from uuid import UUID
from pydantic import BaseModel

from app.database import get_async_session
from app.models.user import User as UserModel
from app.models.document import Document
from app.models.compliance import RegulatoryFramework, RegulatoryRequirement
from app.schemas import DocumentRead, DocumentUploadResponse
from app.services.ai_service import DocumentClassification
from app.core.deps import has_role
from app.services.document_service import DocumentService
from tasks.analysis import process_document


class RenameRequest(BaseModel):
    new_filename: str

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse, tags=["documents"])
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(has_role(["admin"])),
):
    """
    Upload a regulatory document for AI analysis.
    """
    print(f"DEBUG: Uploading document for User {current_user.id}, Tenant {current_user.tenant_id}")
    
    # Validate file
    await DocumentService.validate_file(file)

    # Upload to storage
    storage_path = await DocumentService.upload_to_storage(file, current_user.id)

    # Create database record
    document = await DocumentService.create_document(
        db=db,
        filename=file.filename,
        storage_path=storage_path,
        user_id=current_user.id,
    )
    print(f"DEBUG: Document created in DB: {document.id}")

    # Trigger background analysis (non-blocking)
    try:
        from app.core.celery_app import celery_app
        from tasks.analysis import _process_document_async
        
        if celery_app.conf.task_always_eager:
            print(f"DEBUG: Eager mode detected, awaiting task directly")
            # We are in the event loop, so we must await the async function directly
            # instead of using .delay() which calls asyncio.run()
            await _process_document_async(document.id)
            print("DEBUG: Task completed (eager)")
        else:
            print(f"DEBUG: Triggering process_document.delay({document.id})")
            process_document.delay(str(document.id))
            print("DEBUG: Task triggered successfully")
    except Exception as e:
        # Log but don't fail - document is uploaded, task can be retried
        import logging
        logging.error(f"Failed to queue document processing task: {str(e)}")
        print(f"DEBUG: Task trigger failed: {e}")
        import traceback
        traceback.print_exc()

    # Return response
    return DocumentUploadResponse(
        id=document.id,
        filename=document.filename,
        status=document.status,
        message="File uploaded successfully and is being processed",
    )


@router.get("", response_model=List[DocumentRead], tags=["documents"])
async def list_documents(
    db: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(has_role(["admin", "bpo", "executive"])),
):
    """
    List all documents for the current user's tenant.
    """
    print(f"DEBUG: Listing documents for User {current_user.id}, Tenant {current_user.tenant_id}")
    documents = await DocumentService.get_documents_by_user(
        db=db, user_id=current_user.id, tenant_id=current_user.tenant_id
    )
    
    documents_with_classification = []
    for document in documents:
        classification = None
        if document.regulatory_framework:
            classification = DocumentClassification(
                document_type="Law",
                framework_name=document.regulatory_framework.name,
                framework_description=document.regulatory_framework.description,
                parent_law_name=None,
                version=document.regulatory_framework.version,
            )
        elif document.regulatory_requirement:
            await db.refresh(document.regulatory_requirement, attribute_names=["framework"])
            classification = DocumentClassification(
                document_type="Regulation",
                framework_name=document.regulatory_requirement.name,
                framework_description=document.regulatory_requirement.description,
                parent_law_name=document.regulatory_requirement.framework.name if document.regulatory_requirement.framework else None,
                version=None,
            )
        doc_read = DocumentRead.model_validate(document)
        doc_read.classification = classification
        documents_with_classification.append(doc_read)

    print(f"DEBUG: Found {len(documents_with_classification)} documents")
    return documents_with_classification


@router.get("/{document_id}", response_model=DocumentRead, tags=["documents"])
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(has_role(["admin", "bpo", "executive"])),
):
    """
    Get a specific document by ID.

    - Requires admin, bpo, or executive role
    - Returns document metadata
    """
    document = await DocumentService.get_document_by_id(
        db=db, document_id=document_id, user_id=current_user.id
    )
    # Construct classification if available
    classification = None
    if document.regulatory_framework:
        classification = DocumentClassification(
            document_type="Law",
            framework_name=document.regulatory_framework.name,
            framework_description=document.regulatory_framework.description,
            parent_law_name=None,
            version=document.regulatory_framework.version,
        )
    elif document.regulatory_requirement:
        classification = DocumentClassification(
            document_type="Regulation",
            framework_name=document.regulatory_requirement.name,
            framework_description=document.regulatory_requirement.description,
            parent_law_name=document.regulatory_requirement.framework.name if document.regulatory_requirement.framework else None,
            version=None,
        )

    doc_read = DocumentRead.model_validate(document)
    doc_read.classification = classification
    return doc_read


@router.patch("/{document_id}/rename", response_model=DocumentRead, tags=["documents"])
async def rename_document(
    document_id: UUID,
    request: RenameRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(has_role(["admin"])),
):
    """
    Rename a document.

    - **document_id**: UUID of the document to rename
    - **new_filename**: New filename for the document (in request body)
    - Requires admin role
    - Updates filename in database only (storage path remains unchanged)
    - File extension is preserved automatically
    - Returns updated document metadata
    """
    document = await DocumentService.rename_document(
        db=db,
        document_id=document_id,
        new_filename=request.new_filename,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
    )
    return document


@router.delete("/{document_id}", status_code=status.HTTP_200_OK, tags=["documents"])
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(has_role(["admin"])),
):
    """
    Archive a document (soft delete).

    - **document_id**: UUID of the document to archive
    - Requires admin role
    - Moves document to archive in both database and Supabase storage
    - Returns success message
    """
    await DocumentService.archive_document(
        db=db, document_id=document_id, user_id=current_user.id, tenant_id=current_user.tenant_id
    )
    return {"message": "Document archived successfully"}


@router.post("/{document_id}/process", response_model=DocumentRead, tags=["documents"]) # Updated response_model
async def manually_process_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(has_role(["admin"])),
):
    """
    Manually trigger document processing (for testing/debugging).

    - **document_id**: UUID of the document to process
    - Requires admin role
    - Processes document synchronously and returns detailed status
    - Useful for debugging when automatic processing fails
    """
    import logging
    from tasks.analysis import _process_document_async

    logger = logging.getLogger(__name__)

    # Verify document exists and user has access
    document = await DocumentService.get_document_by_id(
        db=db, document_id=document_id, user_id=current_user.id, tenant_id=current_user.tenant_id
    )

    logger.info(f"Manual processing triggered for document {document_id} by user {current_user.id}")

    # Extract IDs before expiring session to avoid MissingGreenlet on lazy load
    user_id = current_user.id
    tenant_id = current_user.tenant_id

    try:
        # Process document synchronously
        await _process_document_async(document_id)

        # Re-fetch document to get updated status and relationships
        # Use force_refresh=True to bypass identity map and get fresh data from DB
        document = await DocumentService.get_document_by_id(
            db=db, 
            document_id=document_id, 
            user_id=user_id, 
            tenant_id=tenant_id,
            force_refresh=True
        )

        # Construct classification if available
        classification = None
        if document.regulatory_framework:
            classification = DocumentClassification(
                document_type="Law",
                framework_name=document.regulatory_framework.name,
                framework_description=document.regulatory_framework.description,
                parent_law_name=None,
                version=document.regulatory_framework.version,
            )
        elif document.regulatory_requirement:
            classification = DocumentClassification(
                document_type="Regulation",
                framework_name=document.regulatory_requirement.name,
                framework_description=document.regulatory_requirement.description,
                parent_law_name=document.regulatory_requirement.framework.name if document.regulatory_requirement.framework else None,
                version=None,
            )

        doc_read = DocumentRead.model_validate(document)
        doc_read.classification = classification
        return doc_read
    except Exception as e:
        logger.exception(f"Manual processing failed for document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing failed: {str(e)}"
        )
