"""Migrate user_role enum to major_admin / admin / superior_officer / investigator."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "003_rbac_roles"
down_revision: Union[str, None] = "002_investigation_platform"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ADD VALUE must run outside a transaction on some PG versions
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'major_admin'")
        op.execute("ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'superior_officer'")

    op.execute("UPDATE users SET role = 'superior_officer' WHERE role::text = 'supervisor'")
    op.execute("UPDATE users SET role = 'investigator' WHERE role::text = 'forensic_officer'")

    op.create_table(
        "departments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(64), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_departments_name", "departments", ["name"], unique=True)
    op.create_index("ix_departments_code", "departments", ["code"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_departments_code", table_name="departments")
    op.drop_index("ix_departments_name", table_name="departments")
    op.drop_table("departments")
