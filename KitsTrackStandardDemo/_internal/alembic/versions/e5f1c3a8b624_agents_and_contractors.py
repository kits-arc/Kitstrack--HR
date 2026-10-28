"""Organization: agents and contractors, with their agreement files

Revision ID: e5f1c3a8b624
Revises: d4e8b27a91c3
Create Date: 2026-10-28 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import app.db.types


revision: str = 'e5f1c3a8b624'
down_revision: Union[str, None] = 'd4e8b27a91c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'agent',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agent_code', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('kind', sa.String(length=12), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(length=30), nullable=True),
        sa.Column('email', sa.String(length=150), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('agreement_file_name', sa.String(length=200), nullable=True),
        sa.Column('created_at', app.db.types.TZDateTime(), nullable=False),
        sa.Column('updated_at', app.db.types.TZDateTime(), nullable=False),
        sa.CheckConstraint("kind IN ('Agent', 'Contractor')", name='agent_kind_valid'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('agent_code'),
    )
    op.create_table(
        'agent_agreement',
        sa.Column('agent_id', sa.Integer(), nullable=False),
        sa.Column('file_name', sa.String(length=200), nullable=False),
        sa.Column('data', sa.LargeBinary(), nullable=False),
        sa.Column('uploaded_at', app.db.types.TZDateTime(), nullable=False),
        sa.ForeignKeyConstraint(['agent_id'], ['agent.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('agent_id'),
    )


def downgrade() -> None:
    op.drop_table('agent_agreement')
    op.drop_table('agent')
