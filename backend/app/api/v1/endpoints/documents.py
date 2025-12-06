from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from pydantic import BaseModel

from app.database import get_async_session
from app.models.user import User as UserModel
from app.schemas import DocumentRead, DocumentUploadResponse
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

    - **file**: PDF or text file (max 20MB)
    - Requires admin role
    - Returns document metadata with processing status
    """
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

    # Trigger background analysis (non-blocking)
    try:
        process_document.delay(str(document.id))
    except Exception as e:
        # Log but don't fail - document is uploaded, task can be retried
        import logging
        logging.error(f"Failed to queue document processing task: {str(e)}")

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

    - Requires admin, bpo, or executive role
    - Returns documents ordered by creation date (newest first)
    """
    documents = await DocumentService.get_documents_by_user(
        db=db, user_id=current_user.id, tenant_id=current_user.tenant_id
    )
    return documents


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
    return document


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
