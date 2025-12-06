from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
import uuid
from typing import List
from datetime import datetime
import re

from app.models.document import Document, DocumentStatus
from app.schemas import DocumentCreate, DocumentRead
from app.core.supabase import supabase_client
from app.config import settings


class DocumentService:
    """Service for managing document uploads and storage."""

    ALLOWED_MIME_TYPES = {"application/pdf", "text/plain"}
    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB in bytes
    BUCKET_NAME = settings.SUPABASE_STORAGE_BUCKET

    @staticmethod
    async def validate_file(file: UploadFile) -> None:
        """Validate file type and size."""
        # Validate MIME type via header
        if file.content_type not in DocumentService.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type '{file.content_type}' not allowed. Only PDF and text files are supported.",
            )

        # Validate Magic Bytes
        await file.seek(0)
        header = await file.read(1024)  # Read first 1KB
        await file.seek(0)  # Reset pointer

        if file.content_type == "application/pdf":
            if not header.startswith(b"%PDF-"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid PDF file (missing magic bytes).",
                )
        elif file.content_type == "text/plain":
            # Check for binary content (null bytes)
            if b"\x00" in header:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid text file (binary content detected).",
                )

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for Supabase storage (replace spaces and special chars)."""
        # Replace spaces with underscores
        sanitized = filename.replace(" ", "_")
        # Remove or replace other problematic characters, keep alphanumeric, dots, dashes, underscores
        sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', sanitized)
        return sanitized

    @staticmethod
    async def upload_to_storage(file: UploadFile, user_id: UUID) -> str:
        """Upload file to Supabase Storage and return storage path."""
        if not supabase_client:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Storage service not configured",
            )

        # Sanitize filename to remove spaces and special characters
        sanitized_filename = DocumentService.sanitize_filename(file.filename)

        # Generate unique file path while preserving original filename
        # Format: production/{uuid}_{original_filename}
        unique_id = str(uuid.uuid4())
        unique_filename = f"production/{unique_id}_{sanitized_filename}"

        try:
            # Read file content
            content = await file.read()

            # Check file size
            if len(content) > DocumentService.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File size exceeds maximum of {DocumentService.MAX_FILE_SIZE / 1024 / 1024}MB",
                )

            # Upload to Supabase Storage
            response = supabase_client.storage.from_(DocumentService.BUCKET_NAME).upload(
                unique_filename, content, {"content-type": file.content_type}
            )

            # Reset file pointer for potential reuse
            await file.seek(0)

            return unique_filename

        except Exception as e:
            if "already exists" in str(e).lower():
                # File already exists, try with a new UUID
                unique_id = str(uuid.uuid4())
                unique_filename = f"production/{unique_id}_{sanitized_filename}"
                content = await file.read()
                response = supabase_client.storage.from_(DocumentService.BUCKET_NAME).upload(
                    unique_filename, content, {"content-type": file.content_type}
                )
                await file.seek(0)
                return unique_filename
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file to storage: {str(e)}",
            )

    @staticmethod
    async def create_document(
        db: AsyncSession, filename: str, storage_path: str, user_id: UUID
    ) -> Document:
        """Create document record in database."""
        doc_create = DocumentCreate(
            filename=filename,
            storage_path=storage_path,
            uploaded_by=user_id,
            status=DocumentStatus.pending,
        )

        document = Document(
            id=uuid.uuid4(),
            filename=doc_create.filename,
            storage_path=doc_create.storage_path,
            status=doc_create.status,
            uploaded_by=doc_create.uploaded_by,
        )

        db.add(document)
        await db.commit()
        await db.refresh(document)
        return document

    @staticmethod
    async def get_documents_by_user(
        db: AsyncSession, user_id: UUID, tenant_id: UUID
    ) -> List[Document]:
        """Get all non-archived documents uploaded by users in the same tenant."""
        # Join with User table to filter by tenant_id
        # Assuming Document has relationship to User (uploaded_by)
        # And User has tenant_id
        from app.models.user import User

        result = await db.execute(
            select(Document)
            .join(User, Document.uploaded_by == User.id)
            .filter(User.tenant_id == tenant_id)
            .filter(Document.archived_at.is_(None))
            .order_by(Document.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_document_by_id(
        db: AsyncSession, document_id: UUID, user_id: UUID, tenant_id: UUID = None
    ) -> Document:
        """Get a specific document by ID."""
        from app.models.user import User

        result = await db.execute(
            select(Document).filter(Document.id == document_id)
        )
        document = result.scalars().first()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
            )

        # If tenant_id provided, verify user has access via tenant
        if tenant_id is not None:
            # Get document uploader's tenant
            uploader_result = await db.execute(
                select(User).filter(User.id == document.uploaded_by)
            )
            uploader = uploader_result.scalars().first()

            if not uploader or uploader.tenant_id != tenant_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
                )
        else:
            # Verify user has access to this document
            if document.uploaded_by != user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
                )

        return document

    @staticmethod
    async def archive_document(
        db: AsyncSession, document_id: UUID, user_id: UUID, tenant_id: UUID
    ) -> Document:
        """Archive a document (soft delete)."""
        # Get document and verify access
        document = await DocumentService.get_document_by_id(db, document_id, user_id, tenant_id)

        # Check if already archived
        if document.archived_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document is already archived",
            )

        # Archive file in Supabase storage
        await DocumentService.archive_in_storage(document.storage_path)

        # Set archived_at timestamp
        document.archived_at = datetime.utcnow()
        await db.commit()
        await db.refresh(document)

        return document

    @staticmethod
    async def rename_document(
        db: AsyncSession, document_id: UUID, new_filename: str, user_id: UUID, tenant_id: UUID
    ) -> Document:
        """Rename a document (updates filename in database only, not storage path)."""
        # Get document and verify access
        document = await DocumentService.get_document_by_id(db, document_id, user_id, tenant_id)

        # Validate new filename
        if not new_filename or not new_filename.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename cannot be empty",
            )

        # Sanitize the new filename
        sanitized_filename = DocumentService.sanitize_filename(new_filename.strip())

        # Ensure file extension is preserved
        import os
        old_ext = os.path.splitext(document.filename)[1]
        new_ext = os.path.splitext(sanitized_filename)[1]

        # If no extension provided, use the old one
        if not new_ext and old_ext:
            sanitized_filename = f"{sanitized_filename}{old_ext}"

        # Update filename in database (storage_path remains unchanged)
        document.filename = sanitized_filename
        await db.commit()
        await db.refresh(document)

        return document

    @staticmethod
    async def archive_in_storage(storage_path: str) -> None:
        """Move file from active storage to archive folder in Supabase."""
        if not supabase_client:
            # Storage not configured - skip archiving in storage
            return

        try:
            # New path in archive folder
            archive_path = f"archive/{storage_path}"

            # Download the file first
            file_data = supabase_client.storage.from_(DocumentService.BUCKET_NAME).download(storage_path)

            # Upload to archive location
            supabase_client.storage.from_(DocumentService.BUCKET_NAME).upload(
                archive_path, file_data, {"upsert": "true"}
            )

            # Delete from original location
            supabase_client.storage.from_(DocumentService.BUCKET_NAME).remove([storage_path])

        except Exception as e:
            # Log error but don't fail the deletion - file is archived in DB
            import logging
            logging.error(f"Failed to archive file in storage: {str(e)}")
            # Don't raise - allow soft delete to proceed even if storage archive fails
