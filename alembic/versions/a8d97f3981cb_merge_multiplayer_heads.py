"""merge multiplayer heads

Revision ID: a8d97f3981cb
Revises: 42b34864db48, c270ab90d65d
Create Date: 2026-01-23 04:49:26.707729

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a8d97f3981cb'
down_revision: Union[str, None] = ('42b34864db48', 'c270ab90d65d')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
