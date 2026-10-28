"""travel allowance and mess typed per period; fixed OT rate per hour

Revision ID: a41c7e2d9b10
Revises: 3f68dd9d34cb
Create Date: 2026-10-01 18:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import app.db.types


revision: str = 'a41c7e2d9b10'
down_revision: Union[str, None] = '3f68dd9d34cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('employee', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ot_rate_per_hour', app.db.types.DecimalString(length=40), nullable=True))

    with op.batch_alter_table('payroll_input', schema=None) as batch_op:
        batch_op.add_column(sa.Column('travel_allowance', app.db.types.DecimalString(length=40), server_default='0', nullable=False))
        batch_op.add_column(sa.Column('mess_deduction', app.db.types.DecimalString(length=40), server_default='0', nullable=False))


def downgrade() -> None:
    with op.batch_alter_table('payroll_input', schema=None) as batch_op:
        batch_op.drop_column('mess_deduction')
        batch_op.drop_column('travel_allowance')

    with op.batch_alter_table('employee', schema=None) as batch_op:
        batch_op.drop_column('ot_rate_per_hour')
