"""add_archived_at_to_documents

Revision ID: 49ab6f5028d1
Revises: d234567890bc
Create Date: 2025-12-06 19:38:36.052363

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import fastapi_users_db_sqlalchemy


# revision identifiers, used by Alembic.
revision: str = '49ab6f5028d1'
down_revision: Union[str, None] = 'd234567890bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add archived_at column to documents table
    op.add_column('documents', sa.Column('archived_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    # Remove archived_at column from documents table
    op.drop_column('documents', 'archived_at')
