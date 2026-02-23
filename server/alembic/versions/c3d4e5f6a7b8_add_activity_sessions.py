"""add activity_sessions table

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('activity_sessions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('app_name', sa.String(length=255), nullable=False),
        sa.Column('window_title', sa.String(length=2000), nullable=False),
        sa.Column('window_titles', postgresql.JSONB(), nullable=True),
        sa.Column('url', sa.String(length=2000), nullable=True),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_activity_sessions_user_date', 'activity_sessions', ['user_id', 'date'])
    op.create_index('ix_activity_sessions_user_start', 'activity_sessions', ['user_id', 'start_time'])


def downgrade() -> None:
    op.drop_index('ix_activity_sessions_user_start', table_name='activity_sessions')
    op.drop_index('ix_activity_sessions_user_date', table_name='activity_sessions')
    op.drop_table('activity_sessions')
