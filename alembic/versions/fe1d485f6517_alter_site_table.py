"""alter site table

Revision ID: fe1d485f6517
Revises: aa8b71fed4c8
Create Date: 2026-06-20 07:05:00.413428

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fe1d485f6517'
down_revision: Union[str, Sequence[str], None] = 'aa8b71fed4c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('sites', sa.Column('site_content', sa.Integer(), nullable=False))
    op.create_index(op.f('ix_sites_site_content'), 'sites', ['site_content'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_sites_site_content'), table_name='sites')
    op.drop_column('sites', 'site_content')
