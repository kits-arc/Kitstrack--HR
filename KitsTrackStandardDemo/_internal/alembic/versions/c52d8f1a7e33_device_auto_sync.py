"""automatic device sync settings

Revision ID: c52d8f1a7e33
Revises: a41c7e2d9b10
Create Date: 2026-10-02 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import app.db.types


revision: str = 'c52d8f1a7e33'
down_revision: Union[str, None] = 'a41c7e2d9b10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('biometric_device_settings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('auto_sync_enabled', sa.Boolean(), server_default='1', nullable=False))
        batch_op.add_column(sa.Column('auto_sync_minutes', sa.Integer(), server_default='5', nullable=False))
        batch_op.add_column(sa.Column('last_success_at', app.db.types.TZDateTime(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('biometric_device_settings', schema=None) as batch_op:
        batch_op.drop_column('last_success_at')
        batch_op.drop_column('auto_sync_minutes')
        batch_op.drop_column('auto_sync_enabled')
