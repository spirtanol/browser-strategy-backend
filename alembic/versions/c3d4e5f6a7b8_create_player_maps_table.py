"""create player_maps table

Revision ID: c3d4e5f6a7b8
Revises: b8e4c1a0927d
Create Date: 2026-09-19 17:49:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'b8e4c1a0927d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'player_maps',
        sa.Column('player_id', sa.Integer(), nullable=False),
        sa.Column('state', sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], onupdate='NO ACTION', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('player_id'),
    )
    op.execute(sa.text(
        "INSERT INTO player_maps (player_id, state) SELECT id, '{}' FROM players WHERE NOT is_npc"
    ))


def downgrade() -> None:
    op.drop_table('player_maps')
