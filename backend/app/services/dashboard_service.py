"""Dashboard service for aggregating role-specific metrics."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from uuid import UUID
from typing import List

from app.schemas.dashboard import DashboardCard, DashboardMetrics
from app.models.suggestion import AISuggestion, SuggestionStatus
from app.models.compliance import Risk, Control, BusinessProcess


class DashboardService:
    """Service for aggregating dashboard metrics by user role."""

    @staticmethod
    async def get_metrics(
        db: AsyncSession,
        user_id: UUID,
        tenant_id: UUID,
        role: str
    ) -> DashboardMetrics:
        """
        Aggregate role-specific metrics for dashboard display.

        Args:
            db: Database session
            user_id: Current user's ID
            tenant_id: Current user's tenant ID (for RLS filtering)
            role: User's role (admin, bpo, executive, general)

        Returns:
            DashboardMetrics with role-specific cards
        """
        if role == "admin":
            cards = await DashboardService._get_admin_cards(db, tenant_id)
        elif role == "bpo":
            cards = await DashboardService._get_bpo_cards(db, user_id, tenant_id)
        elif role == "executive":
            cards = await DashboardService._get_executive_cards(db, tenant_id)
        else:  # general user
            cards = await DashboardService._get_general_cards(db, tenant_id)

        return DashboardMetrics(user_role=role, cards=cards)

    @staticmethod
    async def _get_admin_cards(db: AsyncSession, tenant_id: UUID) -> List[DashboardCard]:
        """Generate admin-specific dashboard cards."""
        # Admin sees: System Health, User Management, Analyze New Document

        # Count total active risks (example metric for system health)
        risk_count_query = select(func.count(Risk.id)).where(Risk.tenant_id == tenant_id)
        risk_count_result = await db.execute(risk_count_query)
        total_risks = risk_count_result.scalar() or 0

        # Count total active controls
        control_count_query = select(func.count(Control.id)).where(Control.tenant_id == tenant_id)
        control_count_result = await db.execute(control_count_query)
        total_controls = control_count_result.scalar() or 0

        # Count pending suggestions (for triage)
        pending_suggestions_query = select(func.count(AISuggestion.id)).where(
            AISuggestion.status == SuggestionStatus.pending
        )
        pending_result = await db.execute(pending_suggestions_query)
        pending_suggestions = pending_result.scalar() or 0

        return [
            DashboardCard(
                card_id="system_health",
                title="System Health",
                metric=total_risks + total_controls,
                metric_label="items",
                icon="activity",
                action_link="/dashboard/admin/system"
            ),
            DashboardCard(
                card_id="pending_suggestions",
                title="Pending AI Suggestions",
                metric=pending_suggestions,
                metric_label="suggestions",
                icon="inbox",
                action_link="/dashboard/admin/suggestions",
                status="urgent" if pending_suggestions > 10 else None
            ),
            DashboardCard(
                card_id="analyze_document",
                title="Analyze New Document",
                metric=0,
                metric_label="",
                icon="file-text",
                action_link="/dashboard/documents/upload"
            )
        ]

    @staticmethod
    async def _get_bpo_cards(db: AsyncSession, user_id: UUID, tenant_id: UUID) -> List[DashboardCard]:
        """Generate BPO-specific dashboard cards."""
        # BPO sees: Pending Reviews, My Controls, Overdue Assessments

        # Count pending reviews assigned to this BPO
        pending_reviews_query = select(func.count(AISuggestion.id)).where(
            AISuggestion.status == SuggestionStatus.pending_review,
            AISuggestion.assigned_bpo_id == user_id
        )
        pending_reviews_result = await db.execute(pending_reviews_query)
        pending_reviews = pending_reviews_result.scalar() or 0

        # Count controls owned by this BPO
        my_controls_query = select(func.count(Control.id)).where(
            Control.tenant_id == tenant_id,
            Control.owner_id == user_id
        )
        my_controls_result = await db.execute(my_controls_query)
        my_controls = my_controls_result.scalar() or 0

        # Overdue assessments (placeholder - would require assessment_due_date field)
        overdue_assessments = 0  # TODO: Implement when assessment scheduling is added

        return [
            DashboardCard(
                card_id="pending_reviews",
                title="Pending Reviews",
                metric=pending_reviews,
                metric_label="items",
                icon="clipboard-check",
                action_link="/dashboard/bpo/reviews",
                status="urgent" if pending_reviews > 5 else None
            ),
            DashboardCard(
                card_id="my_controls",
                title="My Controls",
                metric=my_controls,
                metric_label="controls",
                icon="shield",
                action_link="/dashboard/controls?owner=me"
            ),
            DashboardCard(
                card_id="overdue_assessments",
                title="Overdue Assessments",
                metric=overdue_assessments,
                metric_label="assessments",
                icon="alert-triangle",
                action_link="/dashboard/bpo/overdue",
                status="urgent" if overdue_assessments > 0 else None
            )
        ]

    @staticmethod
    async def _get_executive_cards(db: AsyncSession, tenant_id: UUID) -> List[DashboardCard]:
        """Generate executive-specific dashboard cards."""
        # Executive sees: Risk Overview, Compliance Status, Recent Activity

        # Count high-priority risks (assuming category field can indicate priority)
        # For MVP, counting all risks as proxy
        total_risks_query = select(func.count(Risk.id)).where(Risk.tenant_id == tenant_id)
        total_risks_result = await db.execute(total_risks_query)
        total_risks = total_risks_result.scalar() or 0

        # Compliance status (placeholder - would require compliance scoring logic)
        compliance_score = 85  # TODO: Implement actual compliance calculation

        # Recent activity (placeholder - count of recent suggestions)
        recent_activity_query = select(func.count(AISuggestion.id))
        recent_activity_result = await db.execute(recent_activity_query)
        recent_activity = recent_activity_result.scalar() or 0

        return [
            DashboardCard(
                card_id="risk_overview",
                title="Risk Overview",
                metric=total_risks,
                metric_label="risks",
                icon="alert-circle",
                action_link="/dashboard/risks"
            ),
            DashboardCard(
                card_id="compliance_status",
                title="Compliance Status",
                metric=compliance_score,
                metric_label="%",
                icon="check-circle",
                action_link="/dashboard/compliance"
            ),
            DashboardCard(
                card_id="recent_activity",
                title="Recent Activity",
                metric=recent_activity,
                metric_label="updates",
                icon="activity",
                action_link="/dashboard/activity"
            )
        ]

    @staticmethod
    async def _get_general_cards(db: AsyncSession, tenant_id: UUID) -> List[DashboardCard]:
        """Generate general user dashboard cards (read-only informational)."""
        # General user sees: Total Risks, Total Controls (read-only)

        total_risks_query = select(func.count(Risk.id)).where(Risk.tenant_id == tenant_id)
        total_risks_result = await db.execute(total_risks_query)
        total_risks = total_risks_result.scalar() or 0

        total_controls_query = select(func.count(Control.id)).where(Control.tenant_id == tenant_id)
        total_controls_result = await db.execute(total_controls_query)
        total_controls = total_controls_result.scalar() or 0

        return [
            DashboardCard(
                card_id="total_risks",
                title="Total Risks",
                metric=total_risks,
                metric_label="risks",
                icon="alert-circle",
                action_link="/dashboard/risks"
            ),
            DashboardCard(
                card_id="total_controls",
                title="Total Controls",
                metric=total_controls,
                metric_label="controls",
                icon="shield",
                action_link="/dashboard/controls"
            )
        ]
