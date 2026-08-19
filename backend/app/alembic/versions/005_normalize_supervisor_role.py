"""Normalize supervisor role to canonical string 'supervisor'."""

from typing import Sequence, Union

from alembic import op

revision: str = "005_normalize_supervisor_role"
down_revision: Union[str, None] = "004_admin_module"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'supervisor'")

    op.execute("UPDATE users SET role = 'supervisor' WHERE role::text IN ('superior_officer', 'superior')")

    op.execute("DELETE FROM roles WHERE code IN ('superior_officer', 'superior') AND EXISTS (SELECT 1 FROM roles WHERE code = 'supervisor')")
    op.execute(
        """
        INSERT INTO roles (id, code, name, description)
        VALUES (gen_random_uuid(), 'supervisor', 'Supervisor', 'Head of investigation / unit supervisor')
        ON CONFLICT (code) DO UPDATE SET name = 'Supervisor', description = 'Head of investigation / unit supervisor'
        """
    )


def downgrade() -> None:
    pass
