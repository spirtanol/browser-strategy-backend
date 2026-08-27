"""create areas table

Revision ID: 5faf2288a883
Revises: a1b2c3d4e5f6
Create Date: 2026-08-20 05:30:31.942060

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5faf2288a883'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'areas',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('x', sa.Float(), nullable=False),
        sa.Column('y', sa.Float(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('empty_duration', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('areas')
