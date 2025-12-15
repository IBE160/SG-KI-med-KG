"""add_document_link_to_frameworks

Revision ID: 854940057530
Revises: 831a8a709deb
Create Date: 2025-12-15 01:21:00.399766

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import fastapi_users_db_sqlalchemy
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '854940057530'
down_revision: Union[str, None] = '831a8a709deb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # RegulatoryFramework
    op.add_column('regulatory_frameworks', sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('fk_regulatory_frameworks_document_id', 'regulatory_frameworks', 'documents', ['document_id'], ['id'])
    
    # RegulatoryRequirement
    op.add_column('regulatory_requirements', sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('fk_regulatory_requirements_document_id', 'regulatory_requirements', 'documents', ['document_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_regulatory_requirements_document_id', 'regulatory_requirements', type_='foreignkey')
    op.drop_column('regulatory_requirements', 'document_id')
    
    op.drop_constraint('fk_regulatory_frameworks_document_id', 'regulatory_frameworks', type_='foreignkey')
    op.drop_column('regulatory_frameworks', 'document_id')
