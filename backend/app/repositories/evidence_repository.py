"""Evidence repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.evidence import Evidence


class EvidenceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, evidence_id: UUID) -> Evidence | None:
        return self.db.scalar(
            select(Evidence).options(joinedload(Evidence.uploaded_by)).where(Evidence.id == evidence_id)
        )

    def list_for_case(
        self,
        case_id: UUID,
        *,
        q: str | None = None,
        file_type: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[Evidence], int]:
        stmt = select(Evidence).options(joinedload(Evidence.uploaded_by)).where(Evidence.case_id == case_id)
        count_stmt = select(func.count()).select_from(Evidence).where(Evidence.case_id == case_id)
        if q:
            like = f"%{q}%"
            filt = or_(Evidence.original_name.ilike(like), Evidence.description.ilike(like), Evidence.filename.ilike(like))
            stmt = stmt.where(filt)
            count_stmt = count_stmt.where(filt)
        if file_type:
            stmt = stmt.where(Evidence.file_type == file_type)
            count_stmt = count_stmt.where(Evidence.file_type == file_type)
        stmt = stmt.order_by(Evidence.upload_date.desc())
        total = self.db.scalar(count_stmt) or 0
        items = list(self.db.scalars(stmt.offset(offset).limit(limit)).unique().all())
        return items, total

    def find_by_hash(self, case_id: UUID, sha256: str) -> Evidence | None:
        return self.db.scalar(
            select(Evidence).where(Evidence.case_id == case_id, Evidence.sha256_hash == sha256)
        )

    def add(self, evidence: Evidence) -> Evidence:
        self.db.add(evidence)
        return evidence

    def delete(self, evidence: Evidence) -> None:
        self.db.delete(evidence)

    def global_search(self, q: str, *, limit: int = 20) -> list[Evidence]:
        like = f"%{q}%"
        stmt = (
            select(Evidence)
            .options(joinedload(Evidence.uploaded_by))
            .where(or_(Evidence.original_name.ilike(like), Evidence.description.ilike(like)))
            .order_by(Evidence.upload_date.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).unique().all())
