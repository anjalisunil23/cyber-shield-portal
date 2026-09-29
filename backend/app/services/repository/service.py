"""Evidence repository catalog: generate, list, import into cases, reset synthetic data."""

from __future__ import annotations

import logging
import mimetypes
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.core.config import get_settings
from app.models.case import Case
from app.models.enums import ActivityAction
from app.models.evidence import Evidence
from app.models.repository import DATASET_NAME, EvidenceRepositoryItem
from app.models.user import User, UserRole
from app.repositories.case_repository import CaseRepository
from app.services.activity import log_activity
from app.services.case_service import CaseService
from app.services.evidence_service import EvidenceService
from app.services.repository.file_factory import relative_repo_path, sha256_bytes, write_repo_file
from app.services.repository.generator import build_dataset, detect_theme

logger = logging.getLogger("cybershield.repository")

CATEGORY_ALIASES = {
    "documents": "documents",
    "document": "documents",
    "images": "images",
    "image": "images",
    "audio": "audio",
    "video": "video",
    "communications": "communications",
    "communication": "communications",
    "chat": "communications",
    "email": "communications",
    "sms": "communications",
    "location": "location",
    "gps": "location",
    "browser": "browser",
    "call logs": "call_logs",
    "call_logs": "call_logs",
    "call_log": "call_logs",
    "cdr": "call_logs",
    "social export": "social_export",
    "social_export": "social_export",
    "social": "social_export",
    "other": "other",
    "metadata": "other",
}


def repository_root() -> Path:
    settings = get_settings()
    root = Path(getattr(settings, "evidence_repository_dir", "") or (Path(settings.upload_dir).parent / "evidence_repository"))
    root.mkdir(parents=True, exist_ok=True)
    return root


class RepositoryService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.cases = CaseRepository(db)

    def _accessible_case_ids(self, user: User) -> list[UUID] | None:
        role = user.role.value if hasattr(user.role, "value") else str(user.role)
        if role in {UserRole.admin.value, UserRole.major_admin.value}:
            return None
        items, _ = self.cases.list(user_id=user.id, user_role=role, user_department_id=user.department_id, limit=500)
        return [c.id for c in items]

    def list_items(
        self,
        user: User,
        *,
        case_id: UUID | None = None,
        category: str | None = None,
        q: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[EvidenceRepositoryItem], int]:
        stmt = (
            select(EvidenceRepositoryItem)
            .options(joinedload(EvidenceRepositoryItem.case))
            .join(Case, Case.id == EvidenceRepositoryItem.case_id)
        )
        count_stmt = (
            select(func.count())
            .select_from(EvidenceRepositoryItem)
            .join(Case, Case.id == EvidenceRepositoryItem.case_id)
        )
        allowed = self._accessible_case_ids(user)
        if allowed is not None:
            stmt = stmt.where(EvidenceRepositoryItem.case_id.in_(allowed or [uuid4()]))
            count_stmt = count_stmt.where(EvidenceRepositoryItem.case_id.in_(allowed or [uuid4()]))
        if case_id:
            stmt = stmt.where(EvidenceRepositoryItem.case_id == case_id)
            count_stmt = count_stmt.where(EvidenceRepositoryItem.case_id == case_id)
        if category and category.lower() not in {"all", "all types", ""}:
            cat = CATEGORY_ALIASES.get(category.lower(), category.lower())
            cat_match = [cat]
            if cat == "call_logs":
                cat_match.extend(["call_log", "communications"])
            if cat == "social_export":
                cat_match.extend(["social", "social_export", "communications"])
            if cat == "browser":
                cat_match.extend(["browser", "communications"])
            if cat == "communications":
                cat_match.extend(["chat_export", "call_logs", "call_log", "social_export", "social", "browser"])
            if cat == "images":
                cat_match.extend(["image", "images"])
            if cat == "audio":
                cat_match.extend(["audio"])
            if cat == "video":
                cat_match.extend(["video"])
            if cat == "documents":
                cat_match.extend(["document", "documents"])
            if cat == "location":
                cat_match.extend(["location", "gps"])
            if cat == "other":
                cat_match.extend(["metadata", "other"])
            stmt = stmt.where(
                or_(
                    EvidenceRepositoryItem.category.in_(cat_match),
                    EvidenceRepositoryItem.file_type.in_(cat_match + [cat.rstrip("s")]),
                )
            )
            count_stmt = count_stmt.where(
                or_(
                    EvidenceRepositoryItem.category.in_(cat_match),
                    EvidenceRepositoryItem.file_type.in_(cat_match + [cat.rstrip("s")]),
                )
            )
        if q and q.strip():
            like = f"%{q.strip()}%"
            filt = or_(
                EvidenceRepositoryItem.filename.ilike(like),
                EvidenceRepositoryItem.original_name.ilike(like),
                EvidenceRepositoryItem.description.ilike(like),
                EvidenceRepositoryItem.category.ilike(like),
                EvidenceRepositoryItem.file_type.ilike(like),
                Case.case_number.ilike(like),
                Case.title.ilike(like),
                cast(EvidenceRepositoryItem.tags, String).ilike(like),
                cast(EvidenceRepositoryItem.metadata_json, String).ilike(like),
            )
            stmt = stmt.where(filt)
            count_stmt = count_stmt.where(filt)
        total = int(self.db.scalar(count_stmt) or 0)
        items = list(
            self.db.scalars(
                stmt.order_by(EvidenceRepositoryItem.created_at.desc()).offset(offset).limit(limit)
            ).unique().all()
        )
        return items, total

    def get(self, item_id: UUID, user: User) -> EvidenceRepositoryItem:
        item = self.db.get(EvidenceRepositoryItem, item_id)
        if not item:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Repository item not found")
        CaseService(self.db).verify_case_access(user, item.case_id)
        return item

    def resolve_path(self, item: EvidenceRepositoryItem) -> Path:
        root = repository_root()
        path = (root / item.storage_path).resolve()
        if not str(path).startswith(str(root.resolve())):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid storage path")
        if not path.exists():
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Repository file missing")
        return path

    def generate_for_case(
        self,
        case_id: UUID,
        actor: User,
        *,
        types: list[str] | None = None,
        count: int | None = None,
        complete: bool = True,
        include_duplicate: bool | None = None,
    ) -> dict[str, Any]:
        case = self.cases.get(case_id)
        if not case:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Case not found")
        CaseService(self.db).verify_case_access(actor, case_id)

        selected = None
        if types:
            selected = {CATEGORY_ALIASES.get(t.lower(), t.lower()) for t in types}
        if include_duplicate is None:
            include_duplicate = case.case_number == "CS-2026-0003" or complete
        files = build_dataset(case, selected=selected, include_duplicate=bool(include_duplicate and complete))

        if count and count > 0 and count < len(files):
            # Fair round-robin distribution across categories present so no type is starved
            by_category: dict[str, list[Any]] = {}
            for f in files:
                cat = f.category or "documents"
                by_category.setdefault(cat, []).append(f)

            balanced_files: list[Any] = []
            category_lists = [list(items) for items in by_category.values()]
            while len(balanced_files) < count and any(category_lists):
                for cat_items in category_lists:
                    if cat_items and len(balanced_files) < count:
                        balanced_files.append(cat_items.pop(0))
            files = balanced_files

        root = repository_root()
        created = []
        refreshed = []
        for spec in files:
            existing = self.db.scalar(
                select(EvidenceRepositoryItem).where(
                    EvidenceRepositoryItem.case_id == case.id,
                    EvidenceRepositoryItem.original_name == spec.filename,
                    EvidenceRepositoryItem.dataset == DATASET_NAME,
                )
            )
            digest = sha256_bytes(spec.data)
            path = write_repo_file(root, case.case_number, spec.category, spec.filename, spec.data)
            if existing:
                existing.filename = spec.filename
                existing.original_name = spec.filename
                existing.file_type = spec.file_type
                existing.category = spec.category
                existing.mime_type = spec.mime_type or mimetypes.guess_type(spec.filename)[0]
                existing.file_size = len(spec.data)
                existing.storage_path = relative_repo_path(root, path)
                existing.sha256_hash = digest
                existing.description = spec.description
                existing.tags = spec.tags
                existing.metadata_json = {
                    "synthetic": True,
                    "dataset": DATASET_NAME,
                    "source": "synthetic_evidence_generator",
                    "theme": detect_theme(case),
                    "entities": spec.entities,
                    "disclaimer": "SYNTHETIC DEMONSTRATION DATA — NOT REAL FORENSIC EVIDENCE",
                }
                refreshed.append(spec.filename)
                continue

            item = EvidenceRepositoryItem(
                case_id=case.id,
                filename=spec.filename,
                original_name=spec.filename,
                file_type=spec.file_type,
                category=spec.category,
                mime_type=spec.mime_type or mimetypes.guess_type(spec.filename)[0],
                file_size=len(spec.data),
                storage_path=relative_repo_path(root, path),
                sha256_hash=digest,
                description=spec.description,
                source_type="synthetic_evidence_generator",
                processing_status="generated",
                synthetic=True,
                dataset=DATASET_NAME,
                tags=spec.tags,
                metadata_json={
                    "synthetic": True,
                    "dataset": DATASET_NAME,
                    "source": "synthetic_evidence_generator",
                    "theme": detect_theme(case),
                    "entities": spec.entities,
                    "disclaimer": "SYNTHETIC DEMONSTRATION DATA — NOT REAL FORENSIC EVIDENCE",
                },
                created_by_id=actor.id,
            )
            self.db.add(item)
            created.append(spec.filename)

        total_ready = len(created) + len(refreshed)
        log_activity(
            self.db,
            user_id=actor.id,
            case_id=case.id,
            actor_role=actor.role.value if hasattr(actor.role, "value") else str(actor.role),
            action=ActivityAction.create,
            resource_type="evidence_repository",
            description=f"Generated/refreshed {total_ready} synthetic repository files for {case.case_number}",
        )
        self.db.commit()
        logger.info(
            "Generated %s new, refreshed %s repository files for %s",
            len(created),
            len(refreshed),
            case.case_number,
        )
        return {
            "success": True,
            "case_id": str(case.id),
            "case_number": case.case_number,
            "theme": detect_theme(case),
            "created": len(created),
            "refreshed": len(refreshed),
            "skipped_existing": len(refreshed),
            "total": total_ready,
            "files": created + refreshed,
            "message": (
                f"Generated {len(created)} new and updated {len(refreshed)} synthetic files for {case.case_number}"
                if len(created) > 0 and len(refreshed) > 0
                else f"Generated {len(created)} synthetic files for {case.case_number}"
                if len(created) > 0
                else f"Refreshed {len(refreshed)} synthetic demonstration files for {case.case_number}"
            ),
            "disclaimer": "SYNTHETIC DEMONSTRATION DATA — NOT REAL FORENSIC EVIDENCE",
        }

    def generate_for_all_cases(self, actor: User, progress: dict[str, Any] | None = None) -> dict[str, Any]:
        cases, _ = self.cases.list(limit=500)
        results = []
        if progress is not None:
            progress["total_cases"] = len(cases)
            progress["status"] = "running"
        for case in cases:
            try:
                res = self.generate_for_case(case.id, actor, complete=True)
                results.append(res)
                if progress is not None:
                    progress["completed"] = progress.get("completed", 0) + 1
                    progress["cases"] = progress.get("cases", []) + [
                        {"case_number": case.case_number, "created": res["created"], "ok": True}
                    ]
            except Exception as exc:
                logger.warning("Repository generate failed for %s: %s", case.case_number, exc)
                results.append({"case_number": case.case_number, "created": 0, "ok": False, "error": str(exc)})
                if progress is not None:
                    progress["cases"] = progress.get("cases", []) + [
                        {"case_number": case.case_number, "created": 0, "ok": False}
                    ]
        total_files = sum(int(r.get("created") or 0) for r in results)
        if progress is not None:
            progress["status"] = "completed"
            progress["total_files"] = total_files
        return {
            "success": True,
            "cases": results,
            "total_files": total_files,
            "disclaimer": "SYNTHETIC DEMONSTRATION DATA — NOT REAL FORENSIC EVIDENCE",
        }

    def add_to_case(self, item_id: UUID, target_case_id: UUID, actor: User) -> Evidence:
        item = self.get(item_id, actor)
        CaseService(self.db).verify_case_access(actor, target_case_id)
        path = self.resolve_path(item)
        data = path.read_bytes()
        evidence = EvidenceService(self.db).ingest_bytes(
            target_case_id,
            item.original_name,
            data,
            actor,
            description=item.description,
            tags=["synthetic_repository", DATASET_NAME, item.category],
            extra_metadata={
                "synthetic": True,
                "dataset": DATASET_NAME,
                "source": "synthetic_evidence_generator",
                "repository_id": str(item.id),
            },
        )
        item.imported_evidence_id = evidence.id
        item.processing_status = "imported"
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return evidence

    def reset_synthetic(self, actor: User) -> dict[str, Any]:
        role = actor.role.value if hasattr(actor.role, "value") else str(actor.role)
        if role not in {UserRole.admin.value, UserRole.major_admin.value}:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Only administrators can reset synthetic data")

        items = list(
            self.db.scalars(
                select(EvidenceRepositoryItem).where(EvidenceRepositoryItem.dataset == DATASET_NAME)
            ).all()
        )
        root = repository_root()
        removed_files = 0
        for item in items:
            try:
                path = root / item.storage_path
                if path.exists():
                    path.unlink()
                    removed_files += 1
            except Exception:
                pass
            self.db.delete(item)

        imported = []
        for ev in self.db.scalars(select(Evidence)).all():
            meta = ev.metadata_json or {}
            tags = ev.tags or []
            if meta.get("dataset") == DATASET_NAME and (
                "synthetic_repository" in tags or meta.get("source") == "synthetic_evidence_generator"
            ):
                imported.append(ev)

        for ev in imported:
            ev.duplicate_of_id = None
        self.db.flush()

        from app.services.storage import get_storage

        storage = get_storage()
        removed_evidence = 0
        for ev in imported:
            try:
                storage.delete(ev.storage_path)
            except Exception:
                pass
            self.db.delete(ev)
            removed_evidence += 1

        log_activity(
            self.db,
            user_id=actor.id,
            actor_role=role,
            action=ActivityAction.delete,
            resource_type="evidence_repository",
            description=f"Reset synthetic repository ({len(items)} catalog items, {removed_evidence} imported evidence)",
        )
        self.db.commit()
        return {
            "success": True,
            "repository_items_deleted": len(items),
            "files_deleted": removed_files,
            "imported_evidence_deleted": removed_evidence,
            "message": "Synthetic repository data removed. Users, cases, and non-synthetic evidence were not deleted.",
        }
