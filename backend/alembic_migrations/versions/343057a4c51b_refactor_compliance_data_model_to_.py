"""refactor compliance data model to framework-requirement hierarchy

Revision ID: 343057a4c51b
Revises: b5a0f0c59e4e
Create Date: 2025-12-12 23:48:52.496278

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = '343057a4c51b'
down_revision: Union[str, None] = 'b5a0f0c59e4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Rename existing regulatory_frameworks to regulatory_requirements_temp
    op.rename_table('regulatory_frameworks', 'regulatory_requirements_temp')

    # Step 2: Create new regulatory_frameworks table (parent/grouping entity)
    op.create_table(
        'regulatory_frameworks',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('version', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )

    # Step 3: Create new regulatory_requirements table (child entity)
    op.create_table(
        'regulatory_requirements',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), nullable=False),
        sa.Column('framework_id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['framework_id'], ['regulatory_frameworks.id'], ondelete='CASCADE')
    )

    # Step 4: Enable RLS on new tables (Supabase-specific)
    op.execute('ALTER TABLE regulatory_frameworks ENABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE regulatory_requirements ENABLE ROW LEVEL SECURITY')

    # Step 5: Create RLS policies for regulatory_frameworks
    op.execute("""
        CREATE POLICY tenant_isolation_select_regulatory_frameworks
        ON regulatory_frameworks
        FOR SELECT
        USING (tenant_id = (SELECT auth.uid()))
    """)
    op.execute("""
        CREATE POLICY tenant_isolation_insert_regulatory_frameworks
        ON regulatory_frameworks
        FOR INSERT
        WITH CHECK (tenant_id = (SELECT auth.uid()))
    """)
    op.execute("""
        CREATE POLICY tenant_isolation_update_regulatory_frameworks
        ON regulatory_frameworks
        FOR UPDATE
        USING (tenant_id = (SELECT auth.uid()))
    """)
    op.execute("""
        CREATE POLICY tenant_isolation_delete_regulatory_frameworks
        ON regulatory_frameworks
        FOR DELETE
        USING (tenant_id = (SELECT auth.uid()))
    """)

    # Step 6: Create RLS policies for regulatory_requirements
    op.execute("""
        CREATE POLICY tenant_isolation_select_regulatory_requirements
        ON regulatory_requirements
        FOR SELECT
        USING (tenant_id = (SELECT auth.uid()))
    """)
    op.execute("""
        CREATE POLICY tenant_isolation_insert_regulatory_requirements
        ON regulatory_requirements
        FOR INSERT
        WITH CHECK (tenant_id = (SELECT auth.uid()))
    """)
    op.execute("""
        CREATE POLICY tenant_isolation_update_regulatory_requirements
        ON regulatory_requirements
        FOR UPDATE
        USING (tenant_id = (SELECT auth.uid()))
    """)
    op.execute("""
        CREATE POLICY tenant_isolation_delete_regulatory_requirements
        ON regulatory_requirements
        FOR DELETE
        USING (tenant_id = (SELECT auth.uid()))
    """)

    # Step 7: Data migration - Create default frameworks and migrate existing requirements
    # Group old "frameworks" (actually requirements) by extracting framework name prefix
    # For now, create a single "Legacy Framework" per tenant and migrate all requirements under it
    op.execute("""
        INSERT INTO regulatory_frameworks (id, tenant_id, name, description, version, created_at, updated_at)
        SELECT
            gen_random_uuid(),
            tenant_id,
            'Legacy Regulatory Framework',
            'Auto-generated framework from data migration. Please update with actual framework details.',
            '1.0',
            NOW(),
            NOW()
        FROM regulatory_requirements_temp
        GROUP BY tenant_id
    """)

    # Step 8: Migrate old requirements to new table, linking to tenant's Legacy Framework
    op.execute("""
        INSERT INTO regulatory_requirements (id, tenant_id, framework_id, name, description, created_at, updated_at)
        SELECT
            rrt.id,
            rrt.tenant_id,
            rf.id,
            rrt.name,
            rrt.description,
            rrt.created_at,
            rrt.updated_at
        FROM regulatory_requirements_temp rrt
        JOIN regulatory_frameworks rf ON rrt.tenant_id = rf.tenant_id AND rf.name = 'Legacy Regulatory Framework'
    """)

    # Step 9: Update junction table foreign key reference
    # Drop old FK constraint pointing to regulatory_requirements_temp
    op.drop_constraint(
        'controls_regulatory_requirements_regulatory_requirement_id_fkey',
        'controls_regulatory_requirements',
        type_='foreignkey'
    )

    # Recreate FK constraint pointing to new regulatory_requirements table
    op.create_foreign_key(
        'controls_regulatory_requirements_regulatory_requirement_id_fkey',
        'controls_regulatory_requirements',
        'regulatory_requirements',
        ['regulatory_requirement_id'],
        ['id'],
        ondelete='CASCADE'
    )

    # Step 10: Drop temporary table
    op.drop_table('regulatory_requirements_temp')

    # Step 11: Create indexes for performance
    op.create_index('ix_regulatory_frameworks_tenant_id', 'regulatory_frameworks', ['tenant_id'])
    op.create_index('ix_regulatory_requirements_tenant_id', 'regulatory_requirements', ['tenant_id'])
    op.create_index('ix_regulatory_requirements_framework_id', 'regulatory_requirements', ['framework_id'])


def downgrade() -> None:
    # Reverse migration: Flatten hierarchy back to single table

    # Step 1: Create temporary table matching old schema
    op.create_table(
        'regulatory_frameworks_temp',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )

    # Step 2: Copy requirements back to old structure (losing framework grouping)
    op.execute("""
        INSERT INTO regulatory_frameworks_temp (id, tenant_id, name, description, created_at, updated_at)
        SELECT id, tenant_id, name, description, created_at, updated_at
        FROM regulatory_requirements
    """)

    # Step 3: Drop indexes
    op.drop_index('ix_regulatory_requirements_framework_id', table_name='regulatory_requirements')
    op.drop_index('ix_regulatory_requirements_tenant_id', table_name='regulatory_requirements')
    op.drop_index('ix_regulatory_frameworks_tenant_id', table_name='regulatory_frameworks')

    # Step 4: Drop new tables
    op.drop_table('regulatory_requirements')
    op.drop_table('regulatory_frameworks')

    # Step 5: Rename temp table back to original name
    op.rename_table('regulatory_frameworks_temp', 'regulatory_frameworks')

    # Step 6: Re-enable RLS on restored table
    op.execute('ALTER TABLE regulatory_frameworks ENABLE ROW LEVEL SECURITY')

    # Step 7: Restore RLS policies (from original migration b5a0f0c59e4e)
    op.execute("""
        CREATE POLICY tenant_isolation_select_regulatory_frameworks
        ON regulatory_frameworks
        FOR SELECT
        USING (tenant_id = (SELECT auth.uid()))
    """)
    op.execute("""
        CREATE POLICY tenant_isolation_insert_regulatory_frameworks
        ON regulatory_frameworks
        FOR INSERT
        WITH CHECK (tenant_id = (SELECT auth.uid()))
    """)
    op.execute("""
        CREATE POLICY tenant_isolation_update_regulatory_frameworks
        ON regulatory_frameworks
        FOR UPDATE
        USING (tenant_id = (SELECT auth.uid()))
    """)
    op.execute("""
        CREATE POLICY tenant_isolation_delete_regulatory_frameworks
        ON regulatory_frameworks
        FOR DELETE
        USING (tenant_id = (SELECT auth.uid()))
    """)
