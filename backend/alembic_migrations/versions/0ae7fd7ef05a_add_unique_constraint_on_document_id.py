"""add_unique_constraint_on_document_id

Revision ID: 0ae7fd7ef05a
Revises: cc7a17bcd1c1
Create Date: 2025-12-15 02:12:59.659667

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import fastapi_users_db_sqlalchemy


# revision identifiers, used by Alembic.
revision: str = '0ae7fd7ef05a'
down_revision: Union[str, None] = 'cc7a17bcd1c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add unique constraint on document_id for regulatory_frameworks
    # This ensures one document can only be linked to one framework
    op.create_unique_constraint(
        'uq_regulatory_frameworks_document_id',
        'regulatory_frameworks',
        ['document_id']
    )

    # Add unique constraint on document_id for regulatory_requirements
    # This ensures one document can only be linked to one requirement
    op.create_unique_constraint(
        'uq_regulatory_requirements_document_id',
        'regulatory_requirements',
        ['document_id']
    )


def downgrade() -> None:
    op.drop_constraint('uq_regulatory_requirements_document_id', 'regulatory_requirements', type_='unique')
    op.drop_constraint('uq_regulatory_frameworks_document_id', 'regulatory_frameworks', type_='unique')
