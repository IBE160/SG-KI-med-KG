"""add ai_suggestions table

Revision ID: ff6256d21065
Revises: 49ab6f5028d1
Create Date: 2025-12-07 02:09:21.891726

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import fastapi_users_db_sqlalchemy


# revision identifiers, used by Alembic.
revision: str = 'ff6256d21065'
down_revision: Union[str, None] = '49ab6f5028d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ai_suggestions table
    op.create_table(
        'ai_suggestions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('document_id', sa.UUID(), nullable=False),
        sa.Column('type', sa.Enum('risk', 'control', name='suggestiontype'), nullable=False),
        sa.Column('content', sa.JSON(), nullable=False),
        sa.Column('rationale', sa.Text(), nullable=False),
        sa.Column('source_reference', sa.Text(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'awaiting_bpo_approval', 'rejected', name='suggestionstatus'), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop ai_suggestions table
    op.drop_table('ai_suggestions')
    op.execute('DROP TYPE suggestiontype')
    op.execute('DROP TYPE suggestionstatus')
