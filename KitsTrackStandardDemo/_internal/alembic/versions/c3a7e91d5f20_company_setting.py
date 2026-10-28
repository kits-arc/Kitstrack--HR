"""company name: one row of installation settings

Revision ID: c3a7e91d5f20
Revises: f85bc7d1a266
Create Date: 2026-10-26 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import app.db.types


revision: str = 'c3a7e91d5f20'
down_revision: Union[str, None] = 'f85bc7d1a266'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'company_setting',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_name', sa.String(length=150), nullable=False),
        sa.Column('updated_at', app.db.types.TZDateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('company_setting')
