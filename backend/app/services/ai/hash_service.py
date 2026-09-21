"""Hash calculation, integrity verification, and duplicate evidence detection."""

from __future__ import annotations

import hashlib
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.evidence import Evidence
from app.repositories.evidence_repository import EvidenceRepository


class HashService:
    @staticmethod
    def calculate_sha256(data: bytes) -> str:
        """Calculate SHA-256 hexadecimal digest for raw byte content."""
        hasher = hashlib.sha256()
        hasher.update(data)
        return hasher.hexdigest()

    @staticmethod
    def check_duplicate(
        db: Session,
        case_id: UUID,
        sha256_hash: str,
        current_evidence_id: UUID | None = None,
    ) -> dict[str, Any]:
        """
        Check whether an evidence file with the same SHA-256 hash already exists in this case.
        Returns duplicate status, matching record id, filename, and warning message.
        """
        repo = EvidenceRepository(db)
        existing = repo.find_by_hash(case_id, sha256_hash)
        
        # If it matches itself during reprocessing, ignore
        if existing and current_evidence_id and existing.id == current_evidence_id:
            return {"is_duplicate": False, "duplicate_of_id": None, "warning": None}

        if existing:
            return {
                "is_duplicate": True,
                "duplicate_of_id": str(existing.id),
                "original_name": existing.original_name,
                "upload_date": existing.upload_date.isoformat() if existing.upload_date else None,
                "warning": (
                    f"Duplicate evidence detected: Matches existing file '{existing.original_name}' "
                    f"(ID: {existing.id}) with identical SHA-256 hash."
                ),
            }
        return {"is_duplicate": False, "duplicate_of_id": None, "warning": None}
