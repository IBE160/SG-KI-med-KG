"""create controls_regulatory_requirements junction table

Revision ID: b5a0f0c59e4e
Revises: 9f36641533ab
Create Date: 2025-12-12 19:12:38.645220

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import fastapi_users_db_sqlalchemy


# revision identifiers, used by Alembic.
revision: str = 'b5a0f0c59e4e'
down_revision: Union[str, None] = '9f36641533ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Detect database dialect
    bind = op.get_bind()
    is_postgresql = bind.dialect.name == "postgresql"

    # Use appropriate types for database
    id_type = sa.UUID() if is_postgresql else sa.String(length=36)
    timestamp_default = (
        sa.text("now()") if is_postgresql else sa.text("CURRENT_TIMESTAMP")
    )

    # Create controls_regulatory_requirements junction table
    op.create_table(
        "controls_regulatory_requirements",
        sa.Column("id", id_type, nullable=False),
        sa.Column("control_id", id_type, nullable=False),
        sa.Column("regulatory_requirement_id", id_type, nullable=False),
        sa.Column("tenant_id", id_type, nullable=False),
        sa.Column("created_by", id_type, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=timestamp_default,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["control_id"],
            ["controls.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["regulatory_requirement_id"],
            ["regulatory_frameworks.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "control_id",
            "regulatory_requirement_id",
            "tenant_id",
            name="unique_control_requirement_per_tenant",
        ),
    )

    # Create indexes for performance
    op.create_index(
        "idx_crr_control_id",
        "controls_regulatory_requirements",
        ["control_id"],
    )
    op.create_index(
        "idx_crr_requirement_id",
        "controls_regulatory_requirements",
        ["regulatory_requirement_id"],
    )
    op.create_index(
        "idx_crr_tenant_id",
        "controls_regulatory_requirements",
        ["tenant_id"],
    )

    # Enable RLS (PostgreSQL only)
    if is_postgresql:
        op.execute(
            "ALTER TABLE controls_regulatory_requirements ENABLE ROW LEVEL SECURITY"
        )

        # Create RLS Policy for tenant isolation
        op.execute("""
            CREATE POLICY "Tenant Access" ON controls_regulatory_requirements
            FOR ALL
            USING (tenant_id = auth.uid())
            WITH CHECK (tenant_id = auth.uid());
        """)


def downgrade() -> None:
    # Detect database dialect
    bind = op.get_bind()
    is_postgresql = bind.dialect.name == "postgresql"

    # Drop RLS Policy (PostgreSQL only)
    if is_postgresql:
        op.execute(
            'DROP POLICY IF EXISTS "Tenant Access" ON controls_regulatory_requirements'
        )

    # Drop indexes
    op.drop_index("idx_crr_tenant_id", table_name="controls_regulatory_requirements")
    op.drop_index(
        "idx_crr_requirement_id", table_name="controls_regulatory_requirements"
    )
    op.drop_index("idx_crr_control_id", table_name="controls_regulatory_requirements")

    # Drop table
    op.drop_table("controls_regulatory_requirements")
