"""enable pgvector

Revision ID: c123456789ab
Revises: b389592974f8
Create Date: 2025-12-02 12:00:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'c123456789ab'
down_revision = 'b389592974f8'
branch_labels = None
depends_on = None


def upgrade():
    # pgvector is PostgreSQL-only; skip for SQLite
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade():
    # pgvector is PostgreSQL-only; skip for SQLite
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.execute("DROP EXTENSION IF EXISTS vector")
