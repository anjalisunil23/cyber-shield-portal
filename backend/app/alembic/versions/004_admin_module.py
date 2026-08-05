"""Admin module: user profile fields, department FK, roles, investigator_assignments."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "004_admin_module"
down_revision: Union[str, None] = "003_rbac_roles"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE notification_type ADD VALUE IF NOT EXISTS 'user_created'")
        op.execute("ALTER TYPE notification_type ADD VALUE IF NOT EXISTS 'case_closed'")
        op.execute("ALTER TYPE activity_action ADD VALUE IF NOT EXISTS 'password_reset'")

    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_roles_code", "roles", ["code"], unique=True)

    op.execute(
        """
        INSERT INTO roles (id, code, name, description) VALUES
        (gen_random_uuid(), 'major_admin', 'Major Admin', 'Platform-level administrator'),
        (gen_random_uuid(), 'admin', 'Admin', 'Department administrator'),
        (gen_random_uuid(), 'superior_officer', 'Superior Officer', 'Head of investigation'),
        (gen_random_uuid(), 'investigator', 'Investigator', 'Field investigator')
        ON CONFLICT (code) DO NOTHING
        """
    )

    # Default department for backfill
    op.execute(
        """
        INSERT INTO departments (id, name, code, description, is_active)
        SELECT gen_random_uuid(), 'Cyber Crime Unit', 'CCU', 'Default investigation unit', true
        WHERE NOT EXISTS (SELECT 1 FROM departments WHERE code = 'CCU')
        """
    )

    op.add_column("users", sa.Column("phone", sa.String(32), nullable=True))
    op.add_column("users", sa.Column("badge_number", sa.String(64), nullable=True))
    op.add_column("users", sa.Column("profile_image_url", sa.String(1024), nullable=True))
    op.add_column("users", sa.Column("department_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index("ix_users_badge_number", "users", ["badge_number"], unique=True)
    op.create_index("ix_users_department_id", "users", ["department_id"])
    op.create_foreign_key(
        "fk_users_department_id",
        "users",
        "departments",
        ["department_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.execute(
        """
        UPDATE users SET department_id = (
            SELECT id FROM departments WHERE code = 'CCU' LIMIT 1
        )
        WHERE department_id IS NULL AND role::text IN ('admin', 'superior_officer', 'investigator')
        """
    )
    op.execute(
        """
        UPDATE users u
        SET department = d.name
        FROM departments d
        WHERE u.department_id = d.id AND (u.department IS NULL OR u.department = '')
        """
    )

    op.add_column("cases", sa.Column("department_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index("ix_cases_department_id", "cases", ["department_id"])
    op.create_foreign_key(
        "fk_cases_department_id",
        "cases",
        "departments",
        ["department_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.execute(
        """
        UPDATE cases c
        SET department_id = u.department_id
        FROM users u
        WHERE c.created_by_id = u.id AND c.department_id IS NULL
        """
    )

    op.create_table(
        "investigator_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("assigned_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("case_id", "user_id", name="uq_investigator_assignment_case_user"),
    )
    op.create_index("ix_investigator_assignments_case_id", "investigator_assignments", ["case_id"])
    op.create_index("ix_investigator_assignments_user_id", "investigator_assignments", ["user_id"])

    # Backfill investigators from case_assignments where role is investigator
    op.execute(
        """
        INSERT INTO investigator_assignments (id, case_id, user_id, assigned_by_id, assigned_at)
        SELECT gen_random_uuid(), ca.case_id, ca.user_id, ca.assigned_by_id, ca.assigned_at
        FROM case_assignments ca
        JOIN users u ON u.id = ca.user_id
        WHERE u.role::text = 'investigator'
        ON CONFLICT (case_id, user_id) DO NOTHING
        """
    )


def downgrade() -> None:
    op.drop_table("investigator_assignments")
    op.drop_constraint("fk_cases_department_id", "cases", type_="foreignkey")
    op.drop_index("ix_cases_department_id", table_name="cases")
    op.drop_column("cases", "department_id")
    op.drop_constraint("fk_users_department_id", "users", type_="foreignkey")
    op.drop_index("ix_users_department_id", table_name="users")
    op.drop_index("ix_users_badge_number", table_name="users")
    op.drop_column("users", "department_id")
    op.drop_column("users", "profile_image_url")
    op.drop_column("users", "badge_number")
    op.drop_column("users", "phone")
    op.drop_index("ix_roles_code", table_name="roles")
    op.drop_table("roles")
