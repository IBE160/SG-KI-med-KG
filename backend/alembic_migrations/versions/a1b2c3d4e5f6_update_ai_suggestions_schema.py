"""update ai_suggestions schema

Revision ID: a1b2c3d4e5f6
Revises: f89141efebf6
Create Date: 2025-12-07 23:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'f89141efebf6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add tenant_id and assigned_bpo_id columns with batch_alter_table for SQLite compatibility
    with op.batch_alter_table('ai_suggestions') as batch_op:
        batch_op.add_column(sa.Column('tenant_id', sa.UUID(), nullable=True))
        batch_op.add_column(sa.Column('assigned_bpo_id', sa.UUID(), nullable=True))
        batch_op.create_foreign_key('fk_ai_suggestions_assigned_bpo_id_user', 'user', ['assigned_bpo_id'], ['id'])

    # 3. Update ENUM values (Postgres only)
    if op.get_context().dialect.name == 'postgresql':
        with op.get_context().autocommit_block():
            op.execute("ALTER TYPE suggestionstatus ADD VALUE IF NOT EXISTS 'pending_review'")
            op.execute("ALTER TYPE suggestionstatus ADD VALUE IF NOT EXISTS 'active'")
            op.execute("ALTER TYPE suggestionstatus ADD VALUE IF NOT EXISTS 'archived'")


def downgrade() -> None:
    # Remove columns with batch_alter_table
    with op.batch_alter_table('ai_suggestions') as batch_op:
        batch_op.drop_constraint('fk_ai_suggestions_assigned_bpo_id_user', type_='foreignkey')
        batch_op.drop_column('assigned_bpo_id')
        batch_op.drop_column('tenant_id')
    
    # Removing ENUM values is not directly supported in Postgres without recreating the type.
    pass
