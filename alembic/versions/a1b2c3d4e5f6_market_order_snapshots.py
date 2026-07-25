"""market_order_snapshots

Revision ID: a1b2c3d4e5f6
Revises: 74681035a9d2
Create Date: 2026-07-25 11:08:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '74681035a9d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'market_order_snapshots',
        sa.Column('id', sa.Integer(), autoincrement=False, nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('platform_id', sa.Integer(), nullable=False),
        sa.Column('order_type', sa.Integer(), nullable=False),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('item_name', sa.String(length=128), nullable=False),
        sa.Column('is_new', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('market_order_snapshots')
