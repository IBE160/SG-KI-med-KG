"""add hierarchy columns (process_id) to risks and controls

Revision ID: c7d8e9f0a1b2
Revises: 343057a4c51b
Create Date: 2025-12-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'c7d8e9f0a1b2'
down_revision: Union[str, None] = '343057a4c51b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add process_id column to risks table
    op.add_column('risks', sa.Column('process_id', UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        'fk_risks_process_id',
        'risks',
        'business_processes',
        ['process_id'],
        ['id']
    )
    op.create_index('ix_risks_process_id', 'risks', ['process_id'])

    # Add process_id column to controls table
    op.add_column('controls', sa.Column('process_id', UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        'fk_controls_process_id',
        'controls',
        'business_processes',
        ['process_id'],
        ['id']
    )
    op.create_index('ix_controls_process_id', 'controls', ['process_id'])


def downgrade() -> None:
    # Remove process_id from controls
    op.drop_index('ix_controls_process_id', table_name='controls')
    op.drop_constraint('fk_controls_process_id', 'controls', type_='foreignkey')
    op.drop_column('controls', 'process_id')

    # Remove process_id from risks
    op.drop_index('ix_risks_process_id', table_name='risks')
    op.drop_constraint('fk_risks_process_id', 'risks', type_='foreignkey')
    op.drop_column('risks', 'process_id')
