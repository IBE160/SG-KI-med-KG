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
    # 1. Add tenant_id column (nullable=True initially to avoid issues with existing rows, 
    # but in a real scenario we'd backfill and set nullable=False)
    op.add_column('ai_suggestions', sa.Column('tenant_id', sa.UUID(), nullable=True))
    
    # 2. Add assigned_bpo_id column
    op.add_column('ai_suggestions', sa.Column('assigned_bpo_id', sa.UUID(), nullable=True))
    op.create_foreign_key('fk_ai_suggestions_assigned_bpo_id_user', 'ai_suggestions', 'user', ['assigned_bpo_id'], ['id'])

    # 3. Update ENUM values
    # PostgreSQL allows adding values to ENUM types inside a transaction (since PG 12)
    # or with commit in between for older versions. 
    # 'pending_review', 'active', 'archived'
    
    # We use execute for ALTER TYPE.
    # Note: verify if we are inside a transaction block. Alembic usually runs in one.
    # ALTER TYPE ... ADD VALUE cannot be run inside a transaction block in some PG versions 
    # unless it's the only statement? actually it's clearer to just execute.
    
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE suggestionstatus ADD VALUE IF NOT EXISTS 'pending_review'")
        op.execute("ALTER TYPE suggestionstatus ADD VALUE IF NOT EXISTS 'active'")
        op.execute("ALTER TYPE suggestionstatus ADD VALUE IF NOT EXISTS 'archived'")


def downgrade() -> None:
    # Remove columns
    op.drop_constraint('fk_ai_suggestions_assigned_bpo_id_user', 'ai_suggestions', type_='foreignkey')
    op.drop_column('ai_suggestions', 'assigned_bpo_id')
    op.drop_column('ai_suggestions', 'tenant_id')
    
    # Removing ENUM values is not directly supported in Postgres without recreating the type.
    # For downgrade, we might just leave the values or accept that we can't easily revert enums.
    pass
