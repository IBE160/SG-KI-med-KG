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
    # Get database connection and inspector to check existing columns
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('ai_suggestions')]

    # 1. Add tenant_id and assigned_bpo_id columns idempotently
    with op.batch_alter_table('ai_suggestions') as batch_op:
        if 'tenant_id' not in columns:
            batch_op.add_column(sa.Column('tenant_id', sa.UUID(), nullable=True))
        
        if 'assigned_bpo_id' not in columns:
            batch_op.add_column(sa.Column('assigned_bpo_id', sa.UUID(), nullable=True))
            # Only create FK if we created the column (or we can assume it's needed)
            # Safe to attempt FK creation if named constraint doesn't exist? 
            # batch_alter_table handles naming usually, but let's be safe.
            batch_op.create_foreign_key('fk_ai_suggestions_assigned_bpo_id_user', 'user', ['assigned_bpo_id'], ['id'])
        else:
            # If column exists, check if FK exists? For simplicity, we assume if column exists, FK might too.
            # But duplicate FK creation usually throws error. 
            # Let's wrap FK in a try/except or just skip if column exists to avoid complex introspection here.
            # Ideally we check constraints too, but this is a hotfix.
            pass

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
