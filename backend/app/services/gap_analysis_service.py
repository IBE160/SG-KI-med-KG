from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from fastapi import HTTPException, status

from app.models.compliance import RegulatoryFramework, RegulatoryRequirement
from app.models.mapping import ControlRegulatoryRequirement
from app.schemas.reports import GapAnalysisReport, UnmappedRequirement


class GapAnalysisService:
    @staticmethod
    async def generate_report(
        db: AsyncSession, framework_id: UUID, tenant_id: UUID
    ) -> GapAnalysisReport:
        """
        Generate a gap analysis report for a regulatory framework.

        Identifies all requirements within the framework and determines which
        have no associated controls (unmapped requirements).

        Args:
            db: Database session
            framework_id: UUID of the regulatory framework (parent entity)
            tenant_id: UUID of the tenant

        Returns:
            GapAnalysisReport: Structured report with coverage metrics and unmapped requirements

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

        # 2. Query all requirements in this framework
        requirements_query = select(RegulatoryRequirement).where(
            and_(
                RegulatoryRequirement.framework_id == framework_id,
                RegulatoryRequirement.tenant_id == tenant_id
            )
        )
        requirements_result = await db.execute(requirements_query)
        all_requirements = requirements_result.scalars().all()

        # 3. Identify unmapped requirements using LEFT JOIN
        # Query to find requirements with no associated controls
        unmapped_query = (
            select(RegulatoryRequirement)
            .outerjoin(
                ControlRegulatoryRequirement,
                and_(
                    ControlRegulatoryRequirement.regulatory_requirement_id == RegulatoryRequirement.id,
                    ControlRegulatoryRequirement.tenant_id == tenant_id
                )
            )
            .where(
                and_(
                    RegulatoryRequirement.framework_id == framework_id,
                    RegulatoryRequirement.tenant_id == tenant_id,
                    ControlRegulatoryRequirement.id.is_(None)  # No mapping exists
                )
            )
        )
        unmapped_result = await db.execute(unmapped_query)
        unmapped_requirements = unmapped_result.scalars().all()

        # 4. Calculate metrics
        total_requirements = len(all_requirements)
        unmapped_count = len(unmapped_requirements)
        mapped_count = total_requirements - unmapped_count
        coverage_percentage = (
            (mapped_count / total_requirements * 100.0) if total_requirements > 0 else 0.0
        )

        # 5. Build gaps list
        gaps = [
            UnmappedRequirement(
                requirement_id=req.id,
                requirement_name=req.name,
                requirement_description=req.description,
                framework_name=framework.name
            )
            for req in unmapped_requirements
        ]

        return GapAnalysisReport(
            framework_id=framework.id,
            framework_name=framework.name,
            total_requirements=total_requirements,
            mapped_requirements=mapped_count,
            unmapped_requirements=unmapped_count,
            coverage_percentage=round(coverage_percentage, 2),
            gaps=gaps
        )
