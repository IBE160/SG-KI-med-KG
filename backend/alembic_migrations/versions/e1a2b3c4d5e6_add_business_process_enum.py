"""add business_process to suggestion type

Revision ID: e1a2b3c4d5e6
Revises: 343057a4c51b
Create Date: 2025-12-13 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e1a2b3c4d5e6'
down_revision: Union[str, None] = '343057a4c51b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use raw SQL to add value to ENUM
    # Note: 'suggestiontype' is the name of the enum type in the DB.
    # We check the dialect to be safe, though this project assumes Postgres for Enums.
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        with op.get_context().autocommit_block():
            op.execute("ALTER TYPE suggestiontype ADD VALUE IF NOT EXISTS 'business_process'")


def downgrade() -> None:
    # Postgres does not support removing values from ENUM types easily.
    pass
