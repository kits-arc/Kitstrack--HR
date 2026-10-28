"""employee profile (gender, e-mail, date of birth, department, designation, photo) and the On Notice / Suspended statuses

Revision ID: d4e8b27a91c3
Revises: c3a7e91d5f20
Create Date: 2026-10-27 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import app.db.types


revision: str = 'd4e8b27a91c3'
down_revision: Union[str, None] = 'c3a7e91d5f20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NEW_STATUSES = "status IN ('active', 'on_notice', 'suspended', 'inactive')"
OLD_STATUSES = "status IN ('active', 'inactive')"


def upgrade() -> None:
    with op.batch_alter_table('employee', schema=None) as batch_op:
        batch_op.add_column(sa.Column('gender', sa.String(length=10), nullable=True))
        batch_op.add_column(sa.Column('email', sa.String(length=150), nullable=True))
        batch_op.add_column(sa.Column('date_of_birth', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('department', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('designation', sa.String(length=100), nullable=True))
        batch_op.drop_constraint('employee_status_valid', type_='check')
        batch_op.create_check_constraint('employee_status_valid', NEW_STATUSES)
    op.create_table(
        'employee_photo',
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('photo', sa.LargeBinary(), nullable=False),
        sa.Column('updated_at', app.db.types.TZDateTime(), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['employee.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('employee_id'),
    )


def downgrade() -> None:
    op.drop_table('employee_photo')
    op.execute("UPDATE employee SET status = 'active' WHERE status IN ('on_notice', 'suspended')")
    with op.batch_alter_table('employee', schema=None) as batch_op:
        batch_op.drop_constraint('employee_status_valid', type_='check')
        batch_op.create_check_constraint('employee_status_valid', OLD_STATUSES)
        batch_op.drop_column('designation')
        batch_op.drop_column('department')
        batch_op.drop_column('date_of_birth')
        batch_op.drop_column('email')
        batch_op.drop_column('gender')
