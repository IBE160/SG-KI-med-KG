import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.services.audit_service import AuditService
from app.models.audit_log import AuditLog
from uuid import uuid4

class MockObj:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

def test_calculate_diff_simple():
    """Test diff calculation for simple field changes."""
    old_obj = MockObj(name="Old Name", description="Old Desc")
    new_data = {"name": "New Name", "description": "Old Desc"}
    
    diff = AuditService.calculate_diff(old_obj, new_data)
    
    assert "name" in diff
    assert diff["name"]["old"] == "Old Name"
    assert diff["name"]["new"] == "New Name"
    assert "description" not in diff

def test_calculate_diff_no_change():
    """Test diff when nothing changes."""
    old_obj = MockObj(name="Same", value=10)
    new_data = {"name": "Same", "value": 10}
    
    diff = AuditService.calculate_diff(old_obj, new_data)
    assert diff == {}

@pytest.mark.asyncio
async def test_log_action_success():
    """Test logging an action persists to DB."""
    mock_db = AsyncMock()
    actor_id = uuid4()
    entity_id = uuid4()
    
    log = await AuditService.log_action(
        mock_db, 
        actor_id, 
        "UPDATE", 
        "Risk", 
        entity_id, 
        changes={"field": {"old": "a", "new": "b"}}
    )
    
    mock_db.add.assert_called_once()
    assert isinstance(log, AuditLog)
    assert log.actor_id == actor_id
    assert log.action == "UPDATE"
    assert log.changes["field"]["new"] == "b"
