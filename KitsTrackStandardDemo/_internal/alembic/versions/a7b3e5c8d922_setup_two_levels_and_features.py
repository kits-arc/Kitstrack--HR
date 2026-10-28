"""Organization setup: two levels (Basic, Standard) and one list of features

Revision ID: a7b3e5c8d922
Revises: f6a2d4b9c711
Create Date: 2026-10-30 09:00:00.000000

"""
import json
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a7b3e5c8d922'
down_revision: Union[str, None] = 'f6a2d4b9c711'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ALL_FEATURES = ("agents", "shift_notifications", "unified_approvals", "manual_permissions", "leave_weekoff", "holiday_calendar", "advance_payments")


def upgrade() -> None:
    with op.batch_alter_table('organization_setup', schema=None) as batch_op:
        batch_op.add_column(sa.Column('features', sa.JSON(), nullable=True))
    bind = op.get_bind()
    rows = bind.execute(sa.text(
        "SELECT id, operating_level, enable_agents, enable_shift_notifications, enable_unified_approvals FROM organization_setup")).fetchall()
    for row_id, level, agents, notices, desk in rows:
        if level == "standard":
            level, features = "standard", {name: True for name in ALL_FEATURES}
        else:                                                    # basic, and the removed "custom" level, become Basic with their switches kept
            level = "basic"
            features = {name: True for name in ALL_FEATURES}
            features.update(agents=bool(agents), shift_notifications=bool(notices), unified_approvals=bool(desk))
        bind.execute(sa.text("UPDATE organization_setup SET features = :features, operating_level = :level WHERE id = :id"),
                     {"features": json.dumps(features), "level": level, "id": row_id})
    with op.batch_alter_table('organization_setup', schema=None) as batch_op:
        batch_op.drop_constraint('setup_level_valid', type_='check')
        batch_op.drop_column('enable_agents')
        batch_op.drop_column('enable_shift_notifications')
        batch_op.drop_column('enable_unified_approvals')
        batch_op.alter_column('features', existing_type=sa.JSON(), nullable=False)
        batch_op.create_check_constraint('setup_level_valid', "operating_level IN ('basic', 'standard')")


def downgrade() -> None:
    with op.batch_alter_table('organization_setup', schema=None) as batch_op:
        batch_op.add_column(sa.Column('enable_agents', sa.Boolean(), nullable=False, server_default=sa.true()))
        batch_op.add_column(sa.Column('enable_shift_notifications', sa.Boolean(), nullable=False, server_default=sa.true()))
        batch_op.add_column(sa.Column('enable_unified_approvals', sa.Boolean(), nullable=False, server_default=sa.true()))
    bind = op.get_bind()
    for row_id, level, features in bind.execute(sa.text("SELECT id, operating_level, features FROM organization_setup")).fetchall():
        flags = json.loads(features) if isinstance(features, str) else (features or {})
        on = level == "standard"
        bind.execute(sa.text("UPDATE organization_setup SET enable_agents = :a, enable_shift_notifications = :n, enable_unified_approvals = :u WHERE id = :id"),
                     {"a": on or bool(flags.get("agents")), "n": on or bool(flags.get("shift_notifications")), "u": on or bool(flags.get("unified_approvals")), "id": row_id})
    with op.batch_alter_table('organization_setup', schema=None) as batch_op:
        batch_op.drop_constraint('setup_level_valid', type_='check')
        batch_op.drop_column('features')
        batch_op.create_check_constraint('setup_level_valid', "operating_level IN ('basic', 'standard', 'custom')")
