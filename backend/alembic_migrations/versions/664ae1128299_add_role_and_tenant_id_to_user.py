"""Add role and tenant_id to User

Revision ID: 664ae1128299
Revises: a8c234ea5923
Create Date: 2025-12-05 15:52:12.035729

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import fastapi_users_db_sqlalchemy


# revision identifiers, used by Alembic.
revision: str = '664ae1128299'
down_revision: Union[str, None] = 'a8c234ea5923'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add role column
    op.add_column('user', sa.Column('role', sa.String(length=50), nullable=False, server_default='general_user'))
    
    # Add tenant_id column. Using a temporary default for existing rows if any.
    # Ideally this should be a real UUID. We'll use a generic one or rely on app logic if table is empty.
    # For 'server_default', postgres supports 'gen_random_uuid()' if pgcrypto is enabled.
    # But we can't assume pgcrypto is enabled (though enable_pgvector migration might have touched extensions).
    # Let's make it nullable=True first for safety in this blind environment, then user can fix data.
    # Or better: Just add it as nullable=True as defined in my plan for MVP stability when I can't test data.
    # Wait, my model said nullable=False. I should try to stick to that if possible.
    # I'll use a placeholder UUID for server_default to avoid NOT NULL violation on existing rows.
    op.add_column('user', sa.Column('tenant_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False, server_default='00000000-0000-0000-0000-000000000000'))


def downgrade() -> None:
    op.drop_column('user', 'tenant_id')
    op.drop_column('user', 'role')