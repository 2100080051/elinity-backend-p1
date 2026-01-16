"""add evaluation_reports table

Revision ID: d4e5f6a7b8c9
Revises: c3b1e2f4a5b6
Create Date: 2025-11-12 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd4e5f6a7b8c9'
down_revision = 'c3b1e2f4a5b6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'evaluation_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('conversation_sessions.id'), nullable=True),
        sa.Column('skill_id', sa.String(), nullable=True),
        sa.Column('skill_type', sa.String(), nullable=True),
        sa.Column('evaluation_json', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('evaluation_reports')
