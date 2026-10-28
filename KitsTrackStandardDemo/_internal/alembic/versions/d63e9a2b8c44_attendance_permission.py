"""manual attendance permissions (late coming, early going, medical)

Revision ID: d63e9a2b8c44
Revises: c52d8f1a7e33
Create Date: 2026-10-06 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import app.db.types


revision: str = 'd63e9a2b8c44'
down_revision: Union[str, None] = 'c52d8f1a7e33'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'attendance_permission',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('permission_date', sa.Date(), nullable=False),
        sa.Column('permission_type', sa.String(length=20), nullable=False),
        sa.Column('minutes_allowed', sa.Integer(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('authorised_by', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('entered_by_user_id', sa.Integer(), nullable=True),
        sa.Column('cancelled_reason', sa.Text(), nullable=True),
        sa.Column('cancelled_by_user_id', sa.Integer(), nullable=True),
        sa.Column('cancelled_at', app.db.types.TZDateTime(), nullable=True),
        sa.Column('created_at', app.db.types.TZDateTime(), nullable=False),
        sa.CheckConstraint("permission_type IN ('late_coming', 'early_going', 'medical', 'other')", name='permission_type_valid'),
        sa.CheckConstraint("status IN ('granted', 'cancelled')", name='permission_status_valid'),
        sa.ForeignKeyConstraint(['employee_id'], ['employee.id']),
        sa.ForeignKeyConstraint(['entered_by_user_id'], ['app_user.id']),
        sa.ForeignKeyConstraint(['cancelled_by_user_id'], ['app_user.id']),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('attendance_permission')
