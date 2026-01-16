"""merge heads ab33a4deb0ad and f6a7b8c9d0e1

Revision ID: m_ab33_f6a7
Revises: ab33a4deb0ad, f6a7b8c9d0e1
Create Date: 2025-12-02 12:00:00.000000
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'm_ab33_f6a7'
down_revision = ('ab33a4deb0ad', 'f6a7b8c9d0e1')
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Merge-only revision: no schema operations. This unifies two heads."""
    pass


def downgrade() -> None:
    """Downgrade is a no-op for this merge revision."""
    pass
