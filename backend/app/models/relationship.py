"""Manual relationship graph edges (AI will populate later)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import EntityKind, RelationshipType

_entity_kind = Enum(EntityKind, name="entity_kind", native_enum=True)


class Relationship(Base):
    __tablename__ = "relationships"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    relationship_type: Mapped[RelationshipType] = mapped_column(
        Enum(RelationshipType, name="relationship_type", native_enum=True),
        nullable=False,
        default=RelationshipType.other,
    )
    source_kind: Mapped[EntityKind] = mapped_column(_entity_kind, nullable=False)
    source_id: Mapped[str] = mapped_column(String(128), nullable=False)
    source_label: Mapped[str] = mapped_column(String(500), nullable=False)
    target_kind: Mapped[EntityKind] = mapped_column(_entity_kind, nullable=False)
    target_id: Mapped[str] = mapped_column(String(128), nullable=False)
    target_label: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    # Phase 2: AI-generated flag / confidence
    ai_generated: Mapped[bool] = mapped_column(default=False, server_default="false")
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    case = relationship("Case", back_populates="relationships_list")
    created_by = relationship("User", foreign_keys=[created_by_id])
