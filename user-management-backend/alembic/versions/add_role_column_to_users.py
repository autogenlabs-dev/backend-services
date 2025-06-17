"""Add role column to users table

Revision ID: add_role_column_to_users
Revises: 6815872ae076
Create Date: 2025-06-03
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_role_column_to_users'
down_revision = '6815872ae076'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('role', sa.String(length=20), nullable=False, server_default='user'))


def downgrade():
    op.drop_column('users', 'role')
