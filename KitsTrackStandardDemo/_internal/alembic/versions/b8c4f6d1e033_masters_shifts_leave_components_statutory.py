"""Version 0.5.0: department / designation masters, shift master, leave types and entitlements, pay components, statutory settings

Revision ID: b8c4f6d1e033
Revises: a7b3e5c8d922
Create Date: 2026-11-05 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import app.db.types


revision: str = 'b8c4f6d1e033'
down_revision: Union[str, None] = 'a7b3e5c8d922'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SHIFT_NAMES = {"A": "Morning", "B": "Afternoon", "C": "Night"}


def upgrade() -> None:
    with op.batch_alter_table('employee', schema=None) as batch_op:
        batch_op.add_column(sa.Column('uan', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('bank_account_number', sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column('bank_ifsc', sa.String(length=15), nullable=True))
        batch_op.add_column(sa.Column('bank_name', sa.String(length=60), nullable=True))
    with op.batch_alter_table('shift_template', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(length=40), nullable=True))
        batch_op.add_column(sa.Column('group_name', sa.String(length=40), nullable=True))
        batch_op.add_column(sa.Column('min_staff', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('max_staff', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), server_default='1', nullable=False))
    with op.batch_alter_table('payroll_line', schema=None) as batch_op:
        batch_op.add_column(sa.Column('other_earnings', app.db.types.DecimalString(), nullable=True))
        batch_op.add_column(sa.Column('other_deductions', app.db.types.DecimalString(), nullable=True))

    bind = op.get_bind()
    for code, name in SHIFT_NAMES.items():
        bind.execute(sa.text("UPDATE shift_template SET name = :name WHERE code = :code AND name IS NULL"), {"name": name, "code": code})
    bind.execute(sa.text("UPDATE shift_template SET name = code WHERE name IS NULL"))

    op.create_table(
        'department',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', app.db.types.TZDateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_table(
        'designation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', app.db.types.TZDateTime(), nullable=False),
        sa.ForeignKeyConstraint(['department_id'], ['department.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_table(
        'department_shift',
        sa.Column('department_id', sa.Integer(), nullable=False),
        sa.Column('shift_template_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['department_id'], ['department.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['shift_template_id'], ['shift_template.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('department_id', 'shift_template_id'),
    )
    op.create_table(
        'leave_type',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('is_paid', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_table(
        'leave_entitlement',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('leave_type_id', sa.Integer(), nullable=False),
        sa.Column('designation_id', sa.Integer(), nullable=True),
        sa.Column('days_per_year', app.db.types.DecimalString(), nullable=False),
        sa.ForeignKeyConstraint(['leave_type_id'], ['leave_type.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['designation_id'], ['designation.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'pay_component_type',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=80), nullable=False),
        sa.Column('kind', sa.String(length=12), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.CheckConstraint("kind IN ('fine', 'deduction', 'incentive', 'bonus')", name='pay_component_kind_valid'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_table(
        'pay_component_entry',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('component_type_id', sa.Integer(), nullable=False),
        sa.Column('entry_date', sa.Date(), nullable=False),
        sa.Column('amount', app.db.types.DecimalString(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=12), nullable=False),
        sa.Column('requested_by_user_id', sa.Integer(), nullable=False),
        sa.Column('requested_at', app.db.types.TZDateTime(), nullable=False),
        sa.Column('decided_by_user_id', sa.Integer(), nullable=True),
        sa.Column('decided_at', app.db.types.TZDateTime(), nullable=True),
        sa.Column('decision_reason', sa.Text(), nullable=True),
        sa.CheckConstraint("status IN ('requested', 'approved', 'rejected', 'cancelled')", name='pay_component_status_valid'),
        sa.ForeignKeyConstraint(['employee_id'], ['employee.id']),
        sa.ForeignKeyConstraint(['component_type_id'], ['pay_component_type.id']),
        sa.ForeignKeyConstraint(['requested_by_user_id'], ['app_user.id']),
        sa.ForeignKeyConstraint(['decided_by_user_id'], ['app_user.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'statutory_setting',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pf_establishment_code', sa.String(length=30), nullable=True),
        sa.Column('esi_establishment_code', sa.String(length=30), nullable=True),
        sa.Column('debit_account_number', sa.String(length=30), nullable=True),
        sa.Column('pt_slabs', sa.JSON(), nullable=False),
        sa.Column('updated_at', app.db.types.TZDateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # Departments and designations already typed on employees become master rows, so nothing has to be entered twice.
    for table, column in (("department", "department"), ("designation", "designation")):
        names = [r[0] for r in bind.execute(sa.text(f"SELECT DISTINCT TRIM({column}) FROM employee WHERE {column} IS NOT NULL AND TRIM({column}) <> ''")).fetchall()]
        seen = set()
        for name in sorted(names):
            if name.lower() in seen:
                continue
            seen.add(name.lower())
            bind.execute(sa.text(f"INSERT INTO {table} (name, is_active, created_at) VALUES (:name, 1, CURRENT_TIMESTAMP)"), {"name": name})
    for name, paid in (("Casual leave", 1), ("Sick leave", 1), ("Earned leave", 1), ("Unpaid leave", 0)):
        bind.execute(sa.text("INSERT INTO leave_type (name, is_paid, is_active) VALUES (:name, :paid, 1)"), {"name": name, "paid": paid})
    for name, kind in (("Late-coming fine", "fine"), ("Damage recovery", "deduction"), ("Production incentive", "incentive"), ("Festival bonus", "bonus")):
        bind.execute(sa.text("INSERT INTO pay_component_type (name, kind, is_active) VALUES (:name, :kind, 1)"), {"name": name, "kind": kind})
    bind.execute(sa.text("INSERT INTO statutory_setting (pt_slabs, updated_at) VALUES ('[]', CURRENT_TIMESTAMP)"))


def downgrade() -> None:
    for table in ('statutory_setting', 'pay_component_entry', 'pay_component_type', 'leave_entitlement', 'leave_type', 'department_shift', 'designation', 'department'):
        op.drop_table(table)
    with op.batch_alter_table('payroll_line', schema=None) as batch_op:
        batch_op.drop_column('other_deductions')
        batch_op.drop_column('other_earnings')
    with op.batch_alter_table('shift_template', schema=None) as batch_op:
        for column in ('is_active', 'max_staff', 'min_staff', 'group_name', 'name'):
            batch_op.drop_column(column)
    with op.batch_alter_table('employee', schema=None) as batch_op:
        for column in ('bank_name', 'bank_ifsc', 'bank_account_number', 'uan'):
            batch_op.drop_column(column)
