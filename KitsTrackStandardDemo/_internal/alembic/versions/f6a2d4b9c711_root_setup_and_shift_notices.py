"""Root login, organization setup (operating level and modules) and shift notices

Revision ID: f6a2d4b9c711
Revises: e5f1c3a8b624
Create Date: 2026-10-29 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import app.db.types


revision: str = 'f6a2d4b9c711'
down_revision: Union[str, None] = 'e5f1c3a8b624'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('app_user', schema=None) as batch_op:
        batch_op.drop_constraint('user_role_valid', type_='check')
        batch_op.create_check_constraint('user_role_valid', "role IN ('ADMIN', 'GM', 'ROOT')")
    op.create_table(
        'organization_setup',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('operating_level', sa.String(length=10), nullable=False),
        sa.Column('enable_agents', sa.Boolean(), nullable=False),
        sa.Column('enable_shift_notifications', sa.Boolean(), nullable=False),
        sa.Column('enable_unified_approvals', sa.Boolean(), nullable=False),
        sa.Column('employee_code_prefix', sa.String(length=10), nullable=False),
        sa.Column('updated_by_user_id', sa.Integer(), nullable=True),
        sa.Column('updated_at', app.db.types.TZDateTime(), nullable=False),
        sa.CheckConstraint("operating_level IN ('basic', 'standard', 'custom')", name='setup_level_valid'),
        sa.ForeignKeyConstraint(['updated_by_user_id'], ['app_user.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'shift_notice',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=10), nullable=False),
        sa.Column('revised', sa.Boolean(), nullable=False),
        sa.Column('channel', sa.String(length=30), nullable=True),
        sa.Column('prepared_by_user_id', sa.Integer(), nullable=True),
        sa.Column('prepared_at', app.db.types.TZDateTime(), nullable=False),
        sa.Column('sent_by_user_id', sa.Integer(), nullable=True),
        sa.Column('sent_at', app.db.types.TZDateTime(), nullable=True),
        sa.CheckConstraint("status IN ('prepared', 'sent')", name='shift_notice_status_valid'),
        sa.ForeignKeyConstraint(['employee_id'], ['employee.id']),
        sa.ForeignKeyConstraint(['prepared_by_user_id'], ['app_user.id']),
        sa.ForeignKeyConstraint(['sent_by_user_id'], ['app_user.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('employee_id', 'period_start', 'period_end', name='shift_notice_unique_period'),
    )


def downgrade() -> None:
    op.drop_table('shift_notice')
    op.drop_table('organization_setup')
    op.execute("DELETE FROM app_user WHERE role = 'ROOT'")
    with op.batch_alter_table('app_user', schema=None) as batch_op:
        batch_op.drop_constraint('user_role_valid', type_='check')
        batch_op.create_check_constraint('user_role_valid', "role IN ('ADMIN', 'GM')")
