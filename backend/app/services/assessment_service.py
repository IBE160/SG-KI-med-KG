"""Service for BPO assessment actions on AI suggestions."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID
from typing import Dict, Optional, Any
import json

from app.models.compliance import BusinessProcess, Risk, Control
from app.models.suggestion import AISuggestion
from app.services.audit_service import AuditService
from app.schemas.assessment import ResidualRisk, AssessmentResponse


class AssessmentService:
    """Handles BPO assessment actions (approve, discard) with audit trail integration.

    All assessment actions are atomic transactions - if audit logging fails,
    the entire transaction is rolled back to ensure data consistency.
    """

    @staticmethod
    async def approve_suggestion(
        db: AsyncSession,
        suggestion_id: UUID,
        residual_risk: ResidualRisk,
        edits: Optional[Dict[str, str]],
        actor_id: UUID,
        tenant_id: UUID
    ) -> AssessmentResponse:
        """Approve a suggestion and create active records in the system.

        Args:
            db: Database session
            suggestion_id: ID of the AI suggestion to approve
            residual_risk: Residual risk categorization (low/medium/high) - REQUIRED
            edits: Optional dictionary with edited field values:
                - edited_risk_description
                - edited_control_description
                - edited_business_process
            actor_id: UUID of the BPO performing the approval
            tenant_id: Tenant ID for multi-tenancy isolation

        Returns:
            AssessmentResponse with success status, message, updated status, and audit log ID

        Raises:
            ValueError: If residual_risk is None or suggestion not found
            SQLAlchemyError: If database operation fails
        """
        if not residual_risk:
            raise ValueError("Residual risk is required for approve action")

        try:
            # Fetch suggestion
            result = await db.execute(
                select(AISuggestion).where(
                    AISuggestion.id == suggestion_id,
                    AISuggestion.tenant_id == tenant_id
                )
            )
            suggestion = result.scalar_one_or_none()

            if not suggestion:
                raise ValueError(f"Suggestion {suggestion_id} not found or not accessible")

            # Optimistic locking: verify suggestion is still pending_review
            if suggestion.status != "pending_review":
                raise ValueError(
                    f"Suggestion {suggestion_id} has status '{suggestion.status}', "
                    "expected 'pending_review'. Cannot approve."
                )

            # Extract AI-suggested data from suggestion.content (JSON field)
            ai_content = suggestion.content if isinstance(suggestion.content, dict) else {}

            # Apply edits if provided, otherwise use AI-suggested values
            business_process_name = (
                edits.get("edited_business_process") if edits
                else ai_content.get("business_process_name", "Unnamed Process")
            )
            risk_description = (
                edits.get("edited_risk_description") if edits
                else ai_content.get("risk_description", suggestion.rationale)
            )
            control_description = (
                edits.get("edited_control_description") if edits
                else ai_content.get("control_description", suggestion.rationale)
            )

            # Create active records
            business_process = BusinessProcess(
                tenant_id=tenant_id,
                name=business_process_name,
                description=f"Business process for {business_process_name}",
                owner_id=actor_id
            )
            db.add(business_process)
            await db.flush()  # Get ID without committing

            risk = Risk(
                tenant_id=tenant_id,
                name=ai_content.get("risk_name", "Unnamed Risk"),
                description=risk_description,
                category=residual_risk.value,  # Use residual_risk for risk category
                owner_id=actor_id
            )
            db.add(risk)
            await db.flush()

            control = Control(
                tenant_id=tenant_id,
                name=ai_content.get("control_name", "Unnamed Control"),
                description=control_description,
                type=ai_content.get("control_type", "Preventive"),
                owner_id=actor_id
            )
            db.add(control)
            await db.flush()

            # Update suggestion status to "active"
            old_status = suggestion.status
            suggestion.status = "active"

            # Prepare audit log changes (include edits if any)
            audit_changes = {
                "action": "approve",
                "residual_risk": residual_risk.value,
                "suggestion_id": str(suggestion_id),
                "created_records": {
                    "business_process_id": str(business_process.id),
                    "risk_id": str(risk.id),
                    "control_id": str(control.id)
                },
                "status_change": {
                    "old": old_status,
                    "new": "active"
                }
            }

            # Add edits to audit log if provided
            if edits:
                original_values = {
                    "business_process": ai_content.get("business_process_name"),
                    "risk_description": ai_content.get("risk_description"),
                    "control_description": ai_content.get("control_description")
                }
                edited_values = {
                    "business_process": edits.get("edited_business_process"),
                    "risk_description": edits.get("edited_risk_description"),
                    "control_description": edits.get("edited_control_description")
                }
                # Calculate diff
                diff = {}
                for key in ["business_process", "risk_description", "control_description"]:
                    if edited_values.get(key) and edited_values[key] != original_values.get(key):
                        diff[key] = {
                            "old": original_values.get(key),
                            "new": edited_values[key]
                        }
                if diff:
                    audit_changes["edits"] = diff

            # Log to audit trail (atomic transaction - if this fails, entire transaction rolls back)
            audit_entry = await AuditService.log_action(
                db=db,
                actor_id=actor_id,
                action="approve_suggestion",
                entity_type="ai_suggestion",
                entity_id=suggestion.id,
                changes=audit_changes
            )

            # Commit transaction
            await db.commit()

            return AssessmentResponse(
                success=True,
                message="Successfully added to register",
                updated_status="active",
                audit_log_id=audit_entry.id,
                active_record_ids={
                    "business_process_id": business_process.id,
                    "risk_id": risk.id,
                    "control_id": control.id
                }
            )

        except SQLAlchemyError as e:
            await db.rollback()
            raise RuntimeError(f"Database error during approval: {str(e)}")
        except Exception as e:
            await db.rollback()
            raise

    @staticmethod
    async def discard_suggestion(
        db: AsyncSession,
        suggestion_id: UUID,
        actor_id: UUID,
        tenant_id: UUID
    ) -> AssessmentResponse:
        """Discard a suggestion by archiving it.

        Args:
            db: Database session
            suggestion_id: ID of the AI suggestion to discard
            actor_id: UUID of the BPO performing the discard
            tenant_id: Tenant ID for multi-tenancy isolation

        Returns:
            AssessmentResponse with success status, message, updated status, and audit log ID

        Raises:
            ValueError: If suggestion not found
            SQLAlchemyError: If database operation fails
        """
        try:
            # Fetch suggestion
            result = await db.execute(
                select(AISuggestion).where(
                    AISuggestion.id == suggestion_id,
                    AISuggestion.tenant_id == tenant_id
                )
            )
            suggestion = result.scalar_one_or_none()

            if not suggestion:
                raise ValueError(f"Suggestion {suggestion_id} not found or not accessible")

            # Optimistic locking: verify suggestion is still pending_review
            if suggestion.status != "pending_review":
                raise ValueError(
                    f"Suggestion {suggestion_id} has status '{suggestion.status}', "
                    "expected 'pending_review'. Cannot discard."
                )

            # Update suggestion status to "archived"
            old_status = suggestion.status
            suggestion.status = "archived"

            # Prepare audit log changes
            audit_changes = {
                "action": "discard",
                "suggestion_id": str(suggestion_id),
                "status_change": {
                    "old": old_status,
                    "new": "archived"
                }
            }

            # Log to audit trail (atomic transaction - if this fails, entire transaction rolls back)
            audit_entry = await AuditService.log_action(
                db=db,
                actor_id=actor_id,
                action="discard_suggestion",
                entity_type="ai_suggestion",
                entity_id=suggestion.id,
                changes=audit_changes
            )

            # Commit transaction
            await db.commit()

            return AssessmentResponse(
                success=True,
                message="Item discarded",
                updated_status="archived",
                audit_log_id=audit_entry.id,
                active_record_ids=None  # No active records created for discard
            )

        except SQLAlchemyError as e:
            await db.rollback()
            raise RuntimeError(f"Database error during discard: {str(e)}")
        except Exception as e:
            await db.rollback()
            raise
