from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.crud.mapping import MappingCRUD
from app.services.audit_service import AuditService
from app.schemas.mapping import MappingDetail, MappingListResponse
from typing import List
from fastapi import HTTPException, status


class MappingService:
    @staticmethod
    async def create_mapping(
        db: AsyncSession,
        control_id: UUID,
        requirement_id: UUID,
        tenant_id: UUID,
        user_id: UUID,
    ) -> MappingDetail:
        """
        Create a new control-to-requirement mapping with validation and audit logging.

        Raises:
            HTTPException 400: If control_id or requirement_id don't exist in tenant
            HTTPException 409: If mapping already exists
        """
        # Validate control exists in tenant
        if not await MappingCRUD.control_exists(db, control_id, tenant_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Control {control_id} not found in tenant"
            )

        # Validate requirement exists in tenant
        if not await MappingCRUD.requirement_exists(db, requirement_id, tenant_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Regulatory requirement {requirement_id} not found in tenant"
            )

        # Check for duplicate mapping
        existing = await MappingCRUD.get_mapping(
            db, control_id, requirement_id, tenant_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Mapping already exists"
            )

        # Create mapping
        mapping = await MappingCRUD.create_mapping(
            db, control_id, requirement_id, tenant_id, user_id
        )

        # Log to audit trail
        await AuditService.log_action(
            db=db,
            actor_id=user_id,
            action="create_mapping",
            entity_type="controls_regulatory_requirements",
            entity_id=mapping.id,
            changes={
                "control_id": str(control_id),
                "regulatory_requirement_id": str(requirement_id),
            },
        )

        # Fetch full details for response
        mappings = await MappingCRUD.get_mappings_for_control(db, control_id, tenant_id)
        # Find the newly created mapping in the results
        for m in mappings:
            if m.id == mapping.id:
                return m

        # Fallback (shouldn't happen, but for safety)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Mapping created but could not retrieve details"
        )

    @staticmethod
    async def delete_mapping(
        db: AsyncSession,
        control_id: UUID,
        requirement_id: UUID,
        tenant_id: UUID,
        user_id: UUID,
    ) -> bool:
        """
        Delete a control-to-requirement mapping with audit logging.

        Returns:
            True if deleted, False if not found (idempotent)

        Raises:
            HTTPException 404: If mapping doesn't exist
        """
        # Get existing mapping for audit log
        existing = await MappingCRUD.get_mapping(
            db, control_id, requirement_id, tenant_id
        )

        # Delete mapping
        deleted = await MappingCRUD.delete_mapping(
            db, control_id, requirement_id, tenant_id
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mapping not found"
            )

        # Log deletion to audit trail
        if existing:
            await AuditService.log_action(
                db=db,
                actor_id=user_id,
                action="delete_mapping",
                entity_type="controls_regulatory_requirements",
                entity_id=existing.id,
                changes={
                    "control_id": str(control_id),
                    "regulatory_requirement_id": str(requirement_id),
                },
            )

        return True

    @staticmethod
    async def get_mappings_for_control(
        db: AsyncSession, control_id: UUID, tenant_id: UUID
    ) -> MappingListResponse:
        """
        Get all regulatory requirements mapped to a specific control.

        Raises:
            HTTPException 404: If control doesn't exist in tenant
        """
        # Validate control exists
        if not await MappingCRUD.control_exists(db, control_id, tenant_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Control {control_id} not found in tenant"
            )

        mappings = await MappingCRUD.get_mappings_for_control(db, control_id, tenant_id)
        return MappingListResponse(total=len(mappings), mappings=mappings)

    @staticmethod
    async def get_mappings_for_requirement(
        db: AsyncSession, requirement_id: UUID, tenant_id: UUID
    ) -> MappingListResponse:
        """
        Get all controls mapped to a specific regulatory requirement.

        Raises:
            HTTPException 404: If requirement doesn't exist in tenant
        """
        # Validate requirement exists
        if not await MappingCRUD.requirement_exists(db, requirement_id, tenant_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Regulatory requirement {requirement_id} not found in tenant"
            )

        mappings = await MappingCRUD.get_mappings_for_requirement(
            db, requirement_id, tenant_id
        )
        return MappingListResponse(total=len(mappings), mappings=mappings)
