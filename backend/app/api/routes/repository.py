"""Synthetic Evidence Repository API."""

from __future__ import annotations

import logging
from typing import Annotated, Any
from uuid import UUID, uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.user import User
from app.schemas.domain import EvidenceOut, PageOut
from app.services.repository.service import RepositoryService
from app.utils.pagination import paginate

logger = logging.getLogger("cybershield.repository")
router = APIRouter(tags=["evidence-repository"])

_JOBS: dict[str, dict[str, Any]] = {}


class RepositoryItemOut(BaseModel):
    id: UUID
    case_id: UUID
    case_number: str | None = None
    case_title: str | None = None
    filename: str
    original_name: str
    file_type: str
    category: str
    mime_type: str | None
    file_size: int
    sha256_hash: str
    description: str | None
    source_type: str
    processing_status: str
    synthetic: bool
    dataset: str
    tags: list[Any] | None = None
    metadata_json: dict[str, Any] | None = None
    imported_evidence_id: UUID | None = None
    created_at: Any
    disclaimer: str = "SYNTHETIC DEMONSTRATION DATA — NOT REAL FORENSIC EVIDENCE"


class GeneratePayload(BaseModel):
    case_id: UUID
    types: list[str] = Field(default_factory=list)
    count: int | None = Field(default=None, ge=1, le=40)
    complete: bool = False


class AddToCasePayload(BaseModel):
    case_id: UUID


def _to_out(item) -> RepositoryItemOut:
    case = getattr(item, "case", None)
    return RepositoryItemOut(
        id=item.id,
        case_id=item.case_id,
        case_number=case.case_number if case else None,
        case_title=case.title if case else None,
        filename=item.filename,
        original_name=item.original_name,
        file_type=item.file_type,
        category=item.category,
        mime_type=item.mime_type,
        file_size=item.file_size,
        sha256_hash=item.sha256_hash,
        description=item.description,
        source_type=item.source_type,
        processing_status=item.processing_status,
        synthetic=item.synthetic,
        dataset=item.dataset,
        tags=item.tags,
        metadata_json=item.metadata_json,
        imported_evidence_id=item.imported_evidence_id,
        created_at=item.created_at,
    )


@router.get("/evidence-repository", response_model=PageOut[RepositoryItemOut])
def list_repository(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    case_id: UUID | None = None,
    category: str | None = None,
    q: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=24, ge=1, le=100),
):
    items, total = RepositoryService(db).list_items(
        user,
        case_id=case_id,
        category=category,
        q=q,
        offset=(page - 1) * page_size,
        limit=page_size,
    )
    return paginate(total, page, page_size, [_to_out(i) for i in items])


@router.get("/evidence-repository/jobs/{job_id}")
def repository_job_status(
    job_id: str,
    _: Annotated[User, Depends(get_current_user)],
):
    job = _JOBS.get(job_id)
    if not job:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


@router.get("/evidence-repository/{item_id}", response_model=RepositoryItemOut)
def get_repository_item(
    item_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    return _to_out(RepositoryService(db).get(item_id, user))


@router.get("/evidence-repository/{item_id}/download")
def download_repository_item(
    item_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    svc = RepositoryService(db)
    item = svc.get(item_id, user)
    path = svc.resolve_path(item)
    return FileResponse(
        path,
        filename=item.original_name,
        media_type=item.mime_type or "application/octet-stream",
    )


@router.get("/evidence-repository/{item_id}/preview")
def preview_repository_item(
    item_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    svc = RepositoryService(db)
    item = svc.get(item_id, user)
    path = svc.resolve_path(item)
    mime = (item.mime_type or "").lower()
    name = (item.original_name or "").lower()
    if mime.startswith(("image/", "audio/", "video/", "application/pdf")) or item.file_type in {"image", "audio", "video"}:
        return FileResponse(path, media_type=item.mime_type or "application/octet-stream")
    text = ""
    try:
        if name.endswith(".docx"):
            import zipfile
            import xml.etree.ElementTree as ET

            with zipfile.ZipFile(path) as zf:
                xml = zf.read("word/document.xml")
            root = ET.fromstring(xml)
            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            text = "\n".join(t.text or "" for t in root.findall(".//w:t", ns))
        else:
            text = path.read_bytes()[:80_000].decode("utf-8", errors="replace")
    except Exception:
        text = ""
    return JSONResponse(
        {
            "id": str(item.id),
            "filename": item.original_name,
            "mime_type": item.mime_type,
            "text": text,
            "disclaimer": "SYNTHETIC DEMONSTRATION DATA — NOT REAL FORENSIC EVIDENCE",
        }
    )


@router.post("/evidence-repository/generate")
def generate_repository(
    payload: GeneratePayload,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    return RepositoryService(db).generate_for_case(
        payload.case_id,
        user,
        types=payload.types or None,
        count=payload.count,
        complete=payload.complete or not payload.types,
    )


@router.post("/evidence-repository/generate-all")
def generate_all_repository(
    background: BackgroundTasks,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_role(["admin", "major_admin"]))],
):
    job_id = str(uuid4())
    progress: dict[str, Any] = {"job_id": job_id, "status": "queued", "completed": 0, "cases": []}
    _JOBS[job_id] = progress

    def _run() -> None:
        from app.db.session import get_engine
        from sqlalchemy.orm import sessionmaker

        Local = sessionmaker(bind=get_engine(), autocommit=False, autoflush=False)
        session = Local()
        try:
            actor = session.get(User, user.id)
            if not actor:
                progress["status"] = "failed"
                return
            RepositoryService(session).generate_for_all_cases(actor, progress=progress)
        except Exception as exc:
            logger.exception("generate-all failed")
            progress["status"] = "failed"
            progress["error"] = str(exc)
        finally:
            session.close()

    background.add_task(_run)
    return {"success": True, "job_id": job_id, "status": "queued"}


@router.post("/evidence-repository/{item_id}/add-to-case", response_model=EvidenceOut)
def add_repository_to_case(
    item_id: UUID,
    payload: AddToCasePayload,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    evidence = RepositoryService(db).add_to_case(item_id, payload.case_id, user)
    out = EvidenceOut.model_validate(evidence)
    out.file_hash = evidence.sha256_hash
    if evidence.is_duplicate and evidence.metadata_json:
        out.warning = evidence.metadata_json.get("duplicate_warning")
    return out


@router.delete("/evidence-repository/synthetic")
def reset_synthetic_repository(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_role(["admin", "major_admin"]))],
):
    return RepositoryService(db).reset_synthetic(user)
