from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from app.models.audit_log import AuditLog
from typing import Any, Dict, Optional
import json

class AuditService:
    @staticmethod
    async def log_action(
        db: AsyncSession,
        actor_id: UUID,
        action: str,
        entity_type: str,
        entity_id: UUID,
        changes: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """
        Log an action to the audit_logs table.
        """
        audit_entry = AuditLog(
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            changes=changes
        )
        db.add(audit_entry)
        # We usually commit in the caller (service/endpoint), but for audit logs 
        # sometimes we want to ensure it persists even if main transaction logic varies.
        # However, standard practice is to join the main transaction.
        # Caller must commit.
        return audit_entry

    @staticmethod
    def calculate_diff(old_obj: Any, new_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate simple diff between an SQLAlchemy object and new data dictionary.
        """
        diff = {}
        for key, value in new_data.items():
            if hasattr(old_obj, key):
                old_val = getattr(old_obj, key)
                if old_val != value:
                    diff[key] = {"old": old_val, "new": value}
        return diff
