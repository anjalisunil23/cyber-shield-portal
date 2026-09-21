"""Synthetic evidence repository catalog.

Revision ID: 012_evidence_repository
Revises: 011_ai_intelligence_support
Create Date: 2026-09-21
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "012_evidence_repository"
down_revision: Union[str, None] = "011_ai_intelligence_support"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "evidence_repository_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("filename", sa.String(512), nullable=False),
        sa.Column("original_name", sa.String(512), nullable=False),
        sa.Column("file_type", sa.String(128), nullable=False),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("mime_type", sa.String(255), nullable=True),
        sa.Column("file_size", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("storage_path", sa.String(1024), nullable=False),
        sa.Column("sha256_hash", sa.String(64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("source_type", sa.String(64), nullable=False, server_default="synthetic_evidence_generator"),
        sa.Column("processing_status", sa.String(32), nullable=False, server_default="generated"),
        sa.Column("synthetic", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("dataset", sa.String(64), nullable=False, server_default="CYBER_SHIELD_DEMO"),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("imported_evidence_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("evidence.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_evidence_repository_items_case_id", "evidence_repository_items", ["case_id"])
    op.create_index("ix_evidence_repository_items_category", "evidence_repository_items", ["category"])
    op.create_index("ix_evidence_repository_items_file_type", "evidence_repository_items", ["file_type"])
    op.create_index("ix_evidence_repository_items_sha256_hash", "evidence_repository_items", ["sha256_hash"])
    op.create_index("ix_evidence_repository_items_dataset", "evidence_repository_items", ["dataset"])


def downgrade() -> None:
    op.drop_index("ix_evidence_repository_items_dataset", table_name="evidence_repository_items")
    op.drop_index("ix_evidence_repository_items_sha256_hash", table_name="evidence_repository_items")
    op.drop_index("ix_evidence_repository_items_file_type", table_name="evidence_repository_items")
    op.drop_index("ix_evidence_repository_items_category", table_name="evidence_repository_items")
    op.drop_index("ix_evidence_repository_items_case_id", table_name="evidence_repository_items")
    op.drop_table("evidence_repository_items")
