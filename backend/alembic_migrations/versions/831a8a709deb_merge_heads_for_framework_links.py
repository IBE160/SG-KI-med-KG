"""merge_heads_for_framework_links

Revision ID: 831a8a709deb
Revises: c7d8e9f0a1b2, ffc27ef450ae
Create Date: 2025-12-15 01:20:51.134557

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import fastapi_users_db_sqlalchemy


# revision identifiers, used by Alembic.
revision: str = '831a8a709deb'
down_revision: Union[str, None] = ('c7d8e9f0a1b2', 'ffc27ef450ae')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
