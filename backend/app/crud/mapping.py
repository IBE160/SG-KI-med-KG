from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import and_, delete
from uuid import UUID
from app.models.mapping import ControlRegulatoryRequirement
from app.models.compliance import Control, RegulatoryFramework
from app.schemas.mapping import MappingDetail
from typing import List, Optional
from datetime import datetime


class MappingCRUD:
    @staticmethod
    async def create_mapping(
        db: AsyncSession,
        control_id: UUID,
        requirement_id: UUID,
        tenant_id: UUID,
        created_by: UUID,
    ) -> ControlRegulatoryRequirement:
        """
        Create a new control-to-requirement mapping.
        Returns the created mapping record.
        """
        mapping = ControlRegulatoryRequirement(
            control_id=control_id,
            regulatory_requirement_id=requirement_id,
            tenant_id=tenant_id,
            created_by=created_by,
        )
        db.add(mapping)
        await db.flush()
        await db.refresh(mapping)
        return mapping

    @staticmethod
    async def get_mapping(
        db: AsyncSession,
        control_id: UUID,
        requirement_id: UUID,
        tenant_id: UUID,
    ) -> Optional[ControlRegulatoryRequirement]:
        """
        Get a specific mapping by control_id and requirement_id.
        Returns None if not found.
        """
        stmt = select(ControlRegulatoryRequirement).where(
            and_(
                ControlRegulatoryRequirement.control_id == control_id,
                ControlRegulatoryRequirement.regulatory_requirement_id == requirement_id,
                ControlRegulatoryRequirement.tenant_id == tenant_id,
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_mapping(
        db: AsyncSession,
        control_id: UUID,
        requirement_id: UUID,
        tenant_id: UUID,
    ) -> bool:
        """
        Delete a mapping.
        Returns True if deleted, False if not found.
        """
        stmt = delete(ControlRegulatoryRequirement).where(
            and_(
                ControlRegulatoryRequirement.control_id == control_id,
                ControlRegulatoryRequirement.regulatory_requirement_id == requirement_id,
                ControlRegulatoryRequirement.tenant_id == tenant_id,
            )
        )
        result = await db.execute(stmt)
        await db.flush()
        return result.rowcount > 0

    @staticmethod
    async def get_mappings_for_control(
        db: AsyncSession, control_id: UUID, tenant_id: UUID
    ) -> List[MappingDetail]:
        """
        Get all regulatory requirements mapped to a specific control.
        Returns list of MappingDetail with requirement names.
        """
        stmt = (
            select(
                ControlRegulatoryRequirement,
                Control.name.label("control_name"),
                RegulatoryFramework.name.label("requirement_name"),
            )
            .join(Control, ControlRegulatoryRequirement.control_id == Control.id)
            .join(
                RegulatoryFramework,
                ControlRegulatoryRequirement.regulatory_requirement_id
                == RegulatoryFramework.id,
            )
            .where(
                and_(
                    ControlRegulatoryRequirement.control_id == control_id,
                    ControlRegulatoryRequirement.tenant_id == tenant_id,
                )
            )
        )
        result = await db.execute(stmt)
        rows = result.all()

        mappings = []
        for row in rows:
            mapping = row[0]
            control_name = row[1]
            requirement_name = row[2]
            mappings.append(
                MappingDetail(
                    id=mapping.id,
                    control_id=mapping.control_id,
                    regulatory_requirement_id=mapping.regulatory_requirement_id,
                    control_name=control_name,
                    requirement_name=requirement_name,
                    created_at=mapping.created_at,
                    created_by=mapping.created_by,
                )
            )
        return mappings

    @staticmethod
    async def get_mappings_for_requirement(
        db: AsyncSession, requirement_id: UUID, tenant_id: UUID
    ) -> List[MappingDetail]:
        """
        Get all controls mapped to a specific regulatory requirement.
        Returns list of MappingDetail with control names.
        """
        stmt = (
            select(
                ControlRegulatoryRequirement,
                Control.name.label("control_name"),
                RegulatoryFramework.name.label("requirement_name"),
            )
            .join(Control, ControlRegulatoryRequirement.control_id == Control.id)
            .join(
                RegulatoryFramework,
                ControlRegulatoryRequirement.regulatory_requirement_id
                == RegulatoryFramework.id,
            )
            .where(
                and_(
                    ControlRegulatoryRequirement.regulatory_requirement_id
                    == requirement_id,
                    ControlRegulatoryRequirement.tenant_id == tenant_id,
                )
            )
        )
        result = await db.execute(stmt)
        rows = result.all()

        mappings = []
        for row in rows:
            mapping = row[0]
            control_name = row[1]
            requirement_name = row[2]
            mappings.append(
                MappingDetail(
                    id=mapping.id,
                    control_id=mapping.control_id,
                    regulatory_requirement_id=mapping.regulatory_requirement_id,
                    control_name=control_name,
                    requirement_name=requirement_name,
                    created_at=mapping.created_at,
                    created_by=mapping.created_by,
                )
            )
        return mappings

    @staticmethod
    async def control_exists(
        db: AsyncSession, control_id: UUID, tenant_id: UUID
    ) -> bool:
        """
        Check if a control exists in the tenant.
        """
        stmt = select(Control).where(
            and_(Control.id == control_id, Control.tenant_id == tenant_id)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def requirement_exists(
        db: AsyncSession, requirement_id: UUID, tenant_id: UUID
    ) -> bool:
        """
        Check if a regulatory requirement exists in the tenant.
        """
        stmt = select(RegulatoryFramework).where(
            and_(
                RegulatoryFramework.id == requirement_id,
                RegulatoryFramework.tenant_id == tenant_id,
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None
