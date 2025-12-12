from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, case
from sqlalchemy.orm import aliased
from fastapi import HTTPException, status

from app.models.compliance import RegulatoryFramework
from app.models.mapping import ControlRegulatoryRequirement
from app.schemas.reports import GapAnalysisReport, UnmappedRequirement


class GapAnalysisService:
    @staticmethod
    async def generate_report(
        db: AsyncSession, framework_id: UUID, tenant_id: UUID
    ) -> GapAnalysisReport:
        """
        Generate a gap analysis report for a specific regulatory framework.
        
        Args:
            db: Database session
            framework_id: UUID of the regulatory framework
            tenant_id: UUID of the tenant
            
        Returns:
            GapAnalysisReport: Structured report with metrics and gap details
            
        Raises:
            HTTPException 404: If framework not found in tenant
        """
        # 1. Verify framework exists in tenant
        framework_query = select(RegulatoryFramework).where(
            and_(
                RegulatoryFramework.id == framework_id,
                RegulatoryFramework.tenant_id == tenant_id
            )
        )
        framework_result = await db.execute(framework_query)
        framework = framework_result.scalar_one_or_none()
        
        if not framework:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Regulatory framework not found"
            )
            
        # 2. Identify unmapped requirements
        # Based on AC logic, we query for THIS specific framework item and check if it has mappings.
        # However, to support the "Report" concept (which implies multiple items), 
        # we might need to check if there are OTHER items that belong to the same "Framework Family".
        # But without a grouping ID, we can only report on this specific ID.
        #
        # Query: LEFT JOIN to find if mappings exist for this ID
        
        # Subquery to count mappings for this specific framework ID
        # We need to know if it is mapped or not.
        
        mapping_query = select(func.count(ControlRegulatoryRequirement.id)).where(
            and_(
                ControlRegulatoryRequirement.regulatory_requirement_id == framework_id,
                ControlRegulatoryRequirement.tenant_id == tenant_id
            )
        )
        mapping_result = await db.execute(mapping_query)
        mapping_count = mapping_result.scalar() or 0
        
        is_mapped = mapping_count > 0
        
        total_requirements = 1
        mapped_requirements = 1 if is_mapped else 0
        unmapped_requirements = 0 if is_mapped else 1
        coverage_percentage = 100.0 if is_mapped else 0.0
        
        gaps = []
        if not is_mapped:
            gaps.append(
                UnmappedRequirement(
                    requirement_id=framework.id,
                    requirement_name=framework.name,
                    requirement_description=framework.description,
                    framework_name=framework.name # Using name as framework name
                )
            )
            
        return GapAnalysisReport(
            framework_id=framework.id,
            framework_name=framework.name,
            total_requirements=total_requirements,
            mapped_requirements=mapped_requirements,
            unmapped_requirements=unmapped_requirements,
            coverage_percentage=coverage_percentage,
            gaps=gaps
        )