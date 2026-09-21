"""Add metadata_json to manual_leads and relationships for AI pipeline explainability.

Revision ID: 011_ai_intelligence_support
Revises: 010_case_hierarchy_and_chat
Create Date: 2026-09-15
"""

from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "011_ai_intelligence_support"
down_revision: Union[str, None] = "010_case_hierarchy_and_chat"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add metadata_json to manual_leads
    op.add_column(
        "manual_leads",
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )

    # 2. Add metadata_json to relationships
    op.add_column(
        "relationships",
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("relationships", "metadata_json")
    op.drop_column("manual_leads", "metadata_json")
