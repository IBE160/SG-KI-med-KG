"""add_document_backrefs_to_frameworks

Revision ID: cc7a17bcd1c1
Revises: 854940057530
Create Date: 2025-12-15 01:30:19.242296

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import fastapi_users_db_sqlalchemy


# revision identifiers, used by Alembic.
revision: str = 'cc7a17bcd1c1'
down_revision: Union[str, None] = '854940057530'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
