"""remote access: server settings, remote devices, API tokens, idempotency and login attempts

Revision ID: f85bc7d1a266
Revises: e74fab3c9d55
Create Date: 2026-10-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import app.db.types


revision: str = 'f85bc7d1a266'
down_revision: Union[str, None] = 'e74fab3c9d55'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'server_setting',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('bind_host', sa.String(length=100), nullable=False),
        sa.Column('port', sa.Integer(), nullable=False),
        sa.Column('tls_enabled', sa.Boolean(), nullable=False),
        sa.Column('tls_hostnames', sa.Text(), nullable=False),
        sa.Column('require_device_approval', sa.Boolean(), nullable=False),
        sa.Column('session_hours', sa.Integer(), nullable=False),
        sa.Column('updated_at', app.db.types.TZDateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'remote_device',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.String(length=64), nullable=False),
        sa.Column('label', sa.String(length=120), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('requested_ip', sa.String(length=64), nullable=True),
        sa.Column('client_version', sa.String(length=30), nullable=True),
        sa.Column('requested_at', app.db.types.TZDateTime(), nullable=False),
        sa.Column('decided_by_user_id', sa.Integer(), nullable=True),
        sa.Column('decided_at', app.db.types.TZDateTime(), nullable=True),
        sa.Column('last_seen_at', app.db.types.TZDateTime(), nullable=True),
        sa.Column('last_username', sa.String(length=50), nullable=True),
        sa.CheckConstraint("status IN ('pending', 'approved', 'revoked')", name='remote_device_status_valid'),
        sa.ForeignKeyConstraint(['decided_by_user_id'], ['app_user.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('device_id'),
    )
    op.create_table(
        'api_token',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('token_hash', sa.String(length=64), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.String(length=64), nullable=True),
        sa.Column('ip', sa.String(length=64), nullable=True),
        sa.Column('created_at', app.db.types.TZDateTime(), nullable=False),
        sa.Column('expires_at', app.db.types.TZDateTime(), nullable=False),
        sa.Column('last_seen_at', app.db.types.TZDateTime(), nullable=False),
        sa.Column('revoked_at', app.db.types.TZDateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['app_user.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_hash'),
    )
    op.create_table(
        'api_idempotency',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('request_id', sa.String(length=64), nullable=False),
        sa.Column('function', sa.String(length=120), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=False),
        sa.Column('response', sa.Text(), nullable=False),
        sa.Column('created_at', app.db.types.TZDateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['app_user.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'request_id', name='api_idempotency_user_request_unique'),
    )
    op.create_table(
        'login_attempt',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('ip', sa.String(length=64), nullable=True),
        sa.Column('succeeded', sa.Boolean(), nullable=False),
        sa.Column('at', app.db.types.TZDateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('login_attempt')
    op.drop_table('api_idempotency')
    op.drop_table('api_token')
    op.drop_table('remote_device')
    op.drop_table('server_setting')
