import pytest
from sqlalchemy import inspect
from app.models.compliance import BusinessProcess, Risk, Control, RegulatoryFramework
from app.models.base import Base

def test_business_process_model_structure():
    """Verify BusinessProcess model has correct columns and types"""
    columns = {c.name: c.type for c in BusinessProcess.__table__.columns}
    
    assert "id" in columns
    assert "tenant_id" in columns
    assert "name" in columns
    assert "description" in columns
    assert "owner_id" in columns
    assert "created_at" in columns
    assert "updated_at" in columns

def test_risk_model_structure():
    """Verify Risk model has correct columns and types"""
    columns = {c.name: c.type for c in Risk.__table__.columns}
    
    assert "id" in columns
    assert "tenant_id" in columns
    assert "name" in columns
    assert "description" in columns
    assert "category" in columns
    assert "owner_id" in columns
    assert "created_at" in columns
    assert "updated_at" in columns

def test_control_model_structure():
    """Verify Control model has correct columns and types"""
    columns = {c.name: c.type for c in Control.__table__.columns}
    
    assert "id" in columns
    assert "tenant_id" in columns
    assert "name" in columns
    assert "description" in columns
    assert "type" in columns
    assert "owner_id" in columns
    assert "created_at" in columns
    assert "updated_at" in columns

def test_regulatory_framework_model_structure():
    """Verify RegulatoryFramework model has correct columns and types"""
    columns = {c.name: c.type for c in RegulatoryFramework.__table__.columns}
    
    assert "id" in columns
    assert "tenant_id" in columns
    assert "name" in columns
    assert "description" in columns
    assert "version" in columns
    assert "created_at" in columns
    assert "updated_at" in columns

def test_models_inherit_from_base():
    """Verify all models inherit from Base"""
    assert issubclass(BusinessProcess, Base)
    assert issubclass(Risk, Base)
    assert issubclass(Control, Base)
    assert issubclass(RegulatoryFramework, Base)
