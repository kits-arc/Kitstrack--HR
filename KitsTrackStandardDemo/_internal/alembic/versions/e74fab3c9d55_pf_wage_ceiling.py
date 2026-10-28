"""PF wage ceiling in the policy

Revision ID: e74fab3c9d55
Revises: d63e9a2b8c44
Create Date: 2026-10-06 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import app.db.types


revision: str = 'e74fab3c9d55'
down_revision: Union[str, None] = 'd63e9a2b8c44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('policy_settings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('pf_wage_ceiling', app.db.types.DecimalString(), server_default='15000', nullable=False))


def downgrade() -> None:
    with op.batch_alter_table('policy_settings', schema=None) as batch_op:
        batch_op.drop_column('pf_wage_ceiling')
