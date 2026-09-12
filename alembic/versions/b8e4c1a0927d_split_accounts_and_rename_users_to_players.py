"""split accounts and rename users to players

Revision ID: b8e4c1a0927d
Revises: 2e57f489bd99
Create Date: 2026-09-11 16:49:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b8e4c1a0927d'
down_revision: Union[str, Sequence[str], None] = '2e57f489bd99'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table('users', 'players')

    op.create_table(
        'accounts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=128), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('token_version', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )

    op.add_column(
        'players',
        sa.Column('account_id', sa.Integer(), nullable=True),
    )

    op.execute(
        sa.text(
            """
            INSERT INTO accounts (email, password_hash, token_version)
            SELECT email, password_hash, token_version
            FROM players
            WHERE is_npc = 0
            """
        )
    )
    op.execute(
        sa.text(
            """
            UPDATE players p
            INNER JOIN accounts a ON a.email = p.email
            SET p.account_id = a.id
            WHERE p.is_npc = 0
            """
        )
    )

    op.create_index('ix_players_account_id', 'players', ['account_id'], unique=True)

    op.drop_index('email', table_name='players')
    op.drop_column('players', 'email')
    op.drop_column('players', 'password_hash')
    op.drop_column('players', 'token_version')


def downgrade() -> None:
    op.add_column(
        'players',
        sa.Column('email', sa.String(length=128), nullable=True),
    )
    op.add_column(
        'players',
        sa.Column('password_hash', sa.String(length=255), nullable=True),
    )
    op.add_column(
        'players',
        sa.Column(
            'token_version',
            sa.Integer(),
            nullable=False,
            server_default='0',
        ),
    )

    op.execute(
        sa.text(
            """
            UPDATE players p
            INNER JOIN accounts a ON a.id = p.account_id
            SET
                p.email = a.email,
                p.password_hash = a.password_hash,
                p.token_version = a.token_version
            """
        )
    )
    op.execute(
        sa.text(
            """
            UPDATE players
            SET
                email = CONCAT('npc+', id, '@nomail.npc'),
                password_hash = NULL,
                token_version = 0
            WHERE email IS NULL
            """
        )
    )

    op.alter_column(
        'players',
        'email',
        existing_type=sa.String(length=128),
        nullable=False,
    )
    op.alter_column(
        'players',
        'token_version',
        existing_type=sa.Integer(),
        nullable=False,
        server_default=None,
    )
    op.create_index('email', 'players', ['email'], unique=True)

    op.drop_index('ix_players_account_id', table_name='players')
    op.drop_column('players', 'account_id')
    op.drop_table('accounts')
    op.rename_table('players', 'users')
