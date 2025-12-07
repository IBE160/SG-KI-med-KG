"""add dashboard performance indexes

Revision ID: f89141efebf6
Revises: ff6256d21065
Create Date: 2025-12-07 11:06:55.339352

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import fastapi_users_db_sqlalchemy


# revision identifiers, used by Alembic.
revision: str = 'f89141efebf6'
down_revision: Union[str, None] = 'ff6256d21065'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create indexes for dashboard query performance optimization
    # These indexes support the DashboardService queries for role-specific metrics

    # Index on risks(tenant_id) for tenant-filtered counts
    op.create_index('ix_risks_tenant_id', 'risks', ['tenant_id'])

    # Index on controls(tenant_id) for tenant-filtered counts
    op.create_index('ix_controls_tenant_id', 'controls', ['tenant_id'])

    # Index on controls(tenant_id, owner_id) for BPO "My Controls" queries
    op.create_index('ix_controls_tenant_owner', 'controls', ['tenant_id', 'owner_id'])

    # Index on ai_suggestions(status) for pending/awaiting counts
    op.create_index('ix_ai_suggestions_status', 'ai_suggestions', ['status'])

    # Index on business_processes(tenant_id) for tenant-filtered queries
    op.create_index('ix_business_processes_tenant_id', 'business_processes', ['tenant_id'])

    # Index on ai_suggestions(status, document_id) for multi-column queries
    # (future optimization for document-specific suggestion queries)
    op.create_index('ix_ai_suggestions_status_document', 'ai_suggestions', ['status', 'document_id'])


def downgrade() -> None:
    # Drop indexes in reverse order
    op.drop_index('ix_ai_suggestions_status_document', table_name='ai_suggestions')
    op.drop_index('ix_business_processes_tenant_id', table_name='business_processes')
    op.drop_index('ix_ai_suggestions_status', table_name='ai_suggestions')
    op.drop_index('ix_controls_tenant_owner', table_name='controls')
    op.drop_index('ix_controls_tenant_id', table_name='controls')
    op.drop_index('ix_risks_tenant_id', table_name='risks')
