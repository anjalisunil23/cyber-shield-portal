"""Synthetic Evidence Repository catalog — library items, not case evidence."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

DATASET_NAME = "CYBER_SHIELD_DEMO"


class EvidenceRepositoryItem(Base):
    __tablename__ = "evidence_repository_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    original_name: Mapped[str] = mapped_column(String(512), nullable=False)
    file_type: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    mime_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    sha256_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False, default="synthetic_evidence_generator")
    processing_status: Mapped[str] = mapped_column(String(32), nullable=False, default="generated")
    synthetic: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    dataset: Mapped[str] = mapped_column(String(64), nullable=False, default=DATASET_NAME, index=True)
    tags: Mapped[list[Any] | None] = mapped_column(JSONB, nullable=True, default=list)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True, default=dict)
    imported_evidence_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("evidence.id", ondelete="SET NULL"), nullable=True
    )
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    case = relationship("Case")
    created_by = relationship("User", foreign_keys=[created_by_id])
