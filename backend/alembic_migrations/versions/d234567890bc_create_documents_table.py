"""create documents table

Revision ID: d234567890bc
Revises: 664ae1128299
Create Date: 2025-12-06 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "d234567890bc"
down_revision = "664ae1128299"
branch_labels = None
depends_on = None


def upgrade():
    # Create documents table
    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("storage_path", sa.String(512), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "processing", "completed", "failed", name="documentstatus"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["uploaded_by"],
            ["user.id"],
        ),
    )

    # Create index on uploaded_by for faster queries
    op.create_index("ix_documents_uploaded_by", "documents", ["uploaded_by"])


def downgrade():
    op.drop_index("ix_documents_uploaded_by", table_name="documents")
    op.drop_table("documents")
    op.execute("DROP TYPE documentstatus")
