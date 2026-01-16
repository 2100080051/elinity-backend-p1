"""add service_keys table

Revision ID: f6a7b8c9d0e1
Revises: d4e5f6a7b8c9
Create Date: 2025-12-02 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f6a7b8c9d0e1'
down_revision = 'd4e5f6a7b8c9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'service_keys',
        sa.Column('id', sa.String(), primary_key=True, nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('key_hash', sa.String(), nullable=False),
        # `created_by` references `tenants.id` in the application model, but the
        # tenants table may not exist yet in all migration timelines (test/dev
        # environments). Avoid adding a hard FK here to prevent failures when
        # running migrations on a fresh DB; the application logic can enforce
        # referential integrity at the app level or a later migration can add
        # the FK once `tenants` exists.
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('service_keys')
