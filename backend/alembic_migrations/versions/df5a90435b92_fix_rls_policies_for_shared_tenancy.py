"""fix_rls_policies_for_shared_tenancy

Revision ID: df5a90435b92
Revises: e1a2b3c4d5e6
Create Date: 2025-12-13 23:20:40.678135

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df5a90435b92'
down_revision: Union[str, None] = 'e1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Detect database dialect
    bind = op.get_bind()
    is_postgresql = bind.dialect.name == "postgresql"

    if is_postgresql:
        # Tables to update
        tables = ["risks", "controls", "business_processes", "regulatory_frameworks"]
        
        for table in tables:
            # Drop old policy
            op.execute(f'DROP POLICY IF EXISTS "Tenant Access" ON {table}')
            
            # Create new policy that looks up tenant_id from public.user
            # This allows users to see data belonging to their assigned tenant
            # independent of whether they created it or not (collaboration).
            op.execute(f"""
                CREATE POLICY "Tenant Access" ON {table}
                FOR ALL
                USING (tenant_id = (SELECT tenant_id FROM public.user WHERE id = auth.uid()))
                WITH CHECK (tenant_id = (SELECT tenant_id FROM public.user WHERE id = auth.uid()));
            """)


def downgrade() -> None:
    # Detect database dialect
    bind = op.get_bind()
    is_postgresql = bind.dialect.name == "postgresql"

    if is_postgresql:
        tables = ["risks", "controls", "business_processes", "regulatory_frameworks"]
        
        for table in tables:
            # Revert to old policy (strict isolation where User IS Tenant)
            op.execute(f'DROP POLICY IF EXISTS "Tenant Access" ON {table}')
            
            op.execute(f"""
                CREATE POLICY "Tenant Access" ON {table}
                FOR ALL
                USING (tenant_id = auth.uid()::uuid)
                WITH CHECK (tenant_id = auth.uid()::uuid);
            """)