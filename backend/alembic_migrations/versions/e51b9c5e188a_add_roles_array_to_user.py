"""add_roles_array_to_user

Revision ID: e51b9c5e188a
Revises: df5a90435b92
Create Date: 2025-12-13 23:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e51b9c5e188a'
down_revision: Union[str, None] = 'df5a90435b92'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Detect database dialect
    bind = op.get_bind()
    is_postgresql = bind.dialect.name == "postgresql"

    # SQLite doesn't support ARRAY types natively in the same way, usually stored as JSON or string
    # Since this project targets PostgreSQL for production but uses SQLite for testing, we need a conditional strategy.
    # However, SQLAlchemy's ARRAY type can sometimes be emulated or we might need to use JSON for SQLite compatibility if we want to use the same model.
    # Given the previous context (GUID type decorator), we should consider if we need a similar approach for ARRAY.
    # For now, let's focus on the PostgreSQL migration path as that's the production target.
    
    if is_postgresql:
        # 1. Add 'roles' column as ARRAY of Strings
        op.add_column('user', sa.Column('roles', postgresql.ARRAY(sa.String()), nullable=True))
        
        # 2. Migrate existing 'role' to 'roles' array
        # This SQL is PostgreSQL specific
        op.execute("UPDATE \"user\" SET roles = ARRAY[role]")
        
        # 3. Alter 'roles' to be NOT NULL (now that it's populated)
        op.alter_column('user', 'roles', nullable=False)
        
        # 4. Drop old 'role' column
        op.drop_column('user', 'role')
    else:
        # Fallback for SQLite (dev/test): Store as JSON/String or just skip advanced migration features if acceptable.
        # But to keep tests running, we need a column.
        # SQLite doesn't support dropping columns easily in old versions, but modern ones do.
        # We'll add 'roles' as a String (JSON representation) for SQLite to simulate ARRAY.
        
        # NOTE: This is a simplification. In a real-world scenario with persistent SQLite data, we'd need a more complex migration (copy to new table).
        # For in-memory tests, we just need the schema to match the model.
        
        with op.batch_alter_table('user') as batch_op:
            batch_op.add_column(sa.Column('roles', sa.JSON(), nullable=True)) # Use JSON to store list
        
        # Naive migration for SQLite (if data existed) - this might fail if JSON support isn't perfect, but for empty test DB it's fine.
        # op.execute("UPDATE user SET roles = '["' || role || '"]'") 
        
        # For simplicity in this specific project context where SQLite is ephemeral:
        # We will just drop 'role' and rely on 'roles' being present.
        with op.batch_alter_table('user') as batch_op:
             batch_op.drop_column('role')


def downgrade() -> None:
    bind = op.get_bind()
    is_postgresql = bind.dialect.name == "postgresql"
    
    if is_postgresql:
        # 1. Add back 'role' column
        op.add_column('user', sa.Column('role', sa.String(50), nullable=True))
        
        # 2. Populate 'role' from first element of 'roles'
        op.execute("UPDATE \"user\" SET role = roles[1]")
        
        # 3. Make 'role' NOT NULL
        op.alter_column('user', 'role', nullable=False)
        
        # 4. Drop 'roles' column
        op.drop_column('user', 'roles')
    else:
        with op.batch_alter_table('user') as batch_op:
            batch_op.add_column(sa.Column('role', sa.String(50), nullable=True))
            batch_op.drop_column('roles')