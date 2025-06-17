"""merge_branches

Revision ID: 3110a000368c
Revises: 813c23621078, add_role_column_to_users
Create Date: 2025-06-03 03:19:31.541719

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3110a000368c'
down_revision: Union[str, None] = ('813c23621078', 'add_role_column_to_users')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
