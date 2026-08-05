"""Create investigation platform tables (cases, evidence, notes, etc.)."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002_investigation_platform"
down_revision: Union[str, None] = "001_create_users"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def _enum(name: str, *values: str):
    return postgresql.ENUM(*values, name=name, create_type=False)


case_priority = _enum("case_priority", "low", "medium", "high", "critical")
case_status = _enum(
    "case_status",
    "open",
    "under_review",
    "evidence_collection",
    "analysis",
    "completed",
    "archived",
)
lead_priority = _enum("lead_priority", "low", "medium", "high", "critical")
lead_status = _enum("lead_status", "open", "in_progress", "closed", "dismissed")
relationship_type = _enum(
    "relationship_type",
    "evidence_to_evidence",
    "evidence_to_person",
    "evidence_to_device",
    "evidence_to_location",
    "person_to_person",
    "person_to_device",
    "other",
)
entity_kind = _enum("entity_kind", "evidence", "person", "device", "location", "other")
timeline_event_type = _enum(
    "timeline_event_type",
    "case_created",
    "case_updated",
    "status_updated",
    "investigator_assigned",
    "evidence_uploaded",
    "evidence_deleted",
    "note_added",
    "note_updated",
    "lead_created",
    "relationship_created",
    "report_generated",
    "manual",
)
notification_type = _enum(
    "notification_type",
    "case_assigned",
    "evidence_uploaded",
    "status_changed",
    "new_note",
    "lead_created",
    "general",
)
activity_action = _enum(
    "activity_action",
    "login",
    "logout",
    "create",
    "update",
    "delete",
    "download",
    "view",
    "export",
)
report_format = _enum("report_format", "pdf", "csv", "html")


def upgrade() -> None:
    bind = op.get_bind()
    for enum in (
        case_priority,
        case_status,
        lead_priority,
        lead_status,
        relationship_type,
        entity_kind,
        timeline_event_type,
        notification_type,
        activity_action,
        report_format,
    ):
        enum.create(bind, checkfirst=True)

    op.create_table(
        "cases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_number", sa.String(64), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("priority", case_priority, nullable=False),
        sa.Column("status", case_status, nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_cases_case_number", "cases", ["case_number"], unique=True)
    op.create_index("ix_cases_status", "cases", ["status"])
    op.create_index("ix_cases_created_by_id", "cases", ["created_by_id"])

    op.create_table(
        "case_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("assigned_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_primary", sa.Boolean(), server_default="false", nullable=False),
    )
    op.create_index("ix_case_assignments_case_id", "case_assignments", ["case_id"])
    op.create_index("ix_case_assignments_user_id", "case_assignments", ["user_id"])

    op.create_table(
        "evidence",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("filename", sa.String(512), nullable=False),
        sa.Column("original_name", sa.String(512), nullable=False),
        sa.Column("file_type", sa.String(128), nullable=False),
        sa.Column("mime_type", sa.String(255), nullable=True),
        sa.Column("file_size", sa.BigInteger(), nullable=False),
        sa.Column("storage_path", sa.String(1024), nullable=False),
        sa.Column("sha256_hash", sa.String(64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("tags", postgresql.JSONB(), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=True),
        sa.Column("uploaded_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("upload_date", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_duplicate", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("duplicate_of_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("evidence.id", ondelete="SET NULL"), nullable=True),
        sa.Column("ocr_text", sa.Text(), nullable=True),
        sa.Column("speech_transcript", sa.Text(), nullable=True),
        sa.Column("extracted_entities", postgresql.JSONB(), nullable=True),
        sa.Column("detected_objects", postgresql.JSONB(), nullable=True),
        sa.Column("detected_faces", postgresql.JSONB(), nullable=True),
        sa.Column("ai_metadata", postgresql.JSONB(), nullable=True),
        sa.Column("embeddings", postgresql.JSONB(), nullable=True),
        sa.Column("risk_score", sa.Float(), nullable=True),
        sa.Column("ai_summary", sa.Text(), nullable=True),
        sa.Column("knowledge_graph_ids", postgresql.JSONB(), nullable=True),
    )
    op.create_index("ix_evidence_case_id", "evidence", ["case_id"])
    op.create_index("ix_evidence_file_type", "evidence", ["file_type"])
    op.create_index("ix_evidence_sha256_hash", "evidence", ["sha256_hash"])
    op.create_index("ix_evidence_uploaded_by_id", "evidence", ["uploaded_by_id"])

    op.create_table(
        "notes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("is_pinned", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_notes_case_id", "notes", ["case_id"])
    op.create_index("ix_notes_author_id", "notes", ["author_id"])

    op.create_table(
        "timeline",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", timeline_event_type, nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("event_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_timeline_case_id", "timeline", ["case_id"])
    op.create_index("ix_timeline_event_at", "timeline", ["event_at"])

    op.create_table(
        "relationships",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("relationship_type", relationship_type, nullable=False),
        sa.Column("source_kind", entity_kind, nullable=False),
        sa.Column("source_id", sa.String(128), nullable=False),
        sa.Column("source_label", sa.String(500), nullable=False),
        sa.Column("target_kind", entity_kind, nullable=False),
        sa.Column("target_id", sa.String(128), nullable=False),
        sa.Column("target_label", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("ai_generated", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_relationships_case_id", "relationships", ["case_id"])

    op.create_table(
        "manual_leads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("priority", lead_priority, nullable=False),
        sa.Column("status", lead_status, nullable=False),
        sa.Column("related_evidence_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("evidence.id", ondelete="SET NULL"), nullable=True),
        sa.Column("assigned_to_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_manual_leads_case_id", "manual_leads", ["case_id"])
    op.create_index("ix_manual_leads_status", "manual_leads", ["status"])
    op.create_index("ix_manual_leads_assigned_to_id", "manual_leads", ["assigned_to_id"])

    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("notification_type", notification_type, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("link", sa.String(512), nullable=True),
        sa.Column("is_read", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index("ix_notifications_created_at", "notifications", ["created_at"])

    op.create_table(
        "activity_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", activity_action, nullable=False),
        sa.Column("resource_type", sa.String(64), nullable=True),
        sa.Column("resource_id", sa.String(128), nullable=True),
        sa.Column("description", sa.String(1000), nullable=False),
        sa.Column("ip_address", sa.String(64), nullable=True),
        sa.Column("user_agent", sa.String(512), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_activity_logs_user_id", "activity_logs", ["user_id"])
    op.create_index("ix_activity_logs_action", "activity_logs", ["action"])
    op.create_index("ix_activity_logs_resource_type", "activity_logs", ["resource_type"])
    op.create_index("ix_activity_logs_created_at", "activity_logs", ["created_at"])

    op.create_table(
        "reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("format", report_format, nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("storage_path", sa.String(1024), nullable=True),
        sa.Column("generated_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("summary_json", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_reports_case_id", "reports", ["case_id"])

    op.create_table(
        "refresh_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(128), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"])
    op.create_index("ix_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"], unique=True)

    op.create_table(
        "password_reset_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(128), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_password_reset_tokens_user_id", "password_reset_tokens", ["user_id"])
    op.create_index("ix_password_reset_tokens_token_hash", "password_reset_tokens", ["token_hash"], unique=True)


def downgrade() -> None:
    for table in (
        "password_reset_tokens",
        "refresh_tokens",
        "reports",
        "activity_logs",
        "notifications",
        "manual_leads",
        "relationships",
        "timeline",
        "notes",
        "evidence",
        "case_assignments",
        "cases",
    ):
        op.drop_table(table)

    bind = op.get_bind()
    for enum in (
        report_format,
        activity_action,
        notification_type,
        timeline_event_type,
        entity_kind,
        relationship_type,
        lead_status,
        lead_priority,
        case_status,
        case_priority,
    ):
        enum.drop(bind, checkfirst=True)
