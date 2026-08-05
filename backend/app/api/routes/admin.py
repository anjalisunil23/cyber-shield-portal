"""Admin module API — department-scoped management for Admin role."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.models.enums import CasePriority, CaseStatus
from app.models.user import User, UserRole
from app.schemas.admin import (
    AdminCaseAssign,
    AdminCaseCreate,
    AdminCaseOut,
    AdminCaseUpdate,
    AdminDashboardStats,
    AdminPasswordReset,
    AdminReportOut,
    AdminReportRequest,
    AdminUserCreate,
    AdminUserOut,
    AdminUserUpdate,
    EvidenceAdminOut,
    StorageUsageOut,
)
from app.schemas.domain import ActivityOut, PageOut, ReportOut
from app.services.admin_service import (
    AdminCaseService,
    AdminDashboardService,
    AdminEvidenceService,
    AdminReportService,
    AdminUserService,
)
from app.utils.pagination import paginate

router = APIRouter(prefix="/admin", tags=["admin"])

AdminUser = Annotated[User, Depends(require_role(["admin", "major_admin"]))]


@router.get("/dashboard", response_model=AdminDashboardStats)
def admin_dashboard(db: Annotated[Session, Depends(get_db)], actor: AdminUser):
    return AdminDashboardService(db).stats(actor)


@router.get("/users", response_model=PageOut[AdminUserOut])
def list_admin_users(
    db: Annotated[Session, Depends(get_db)],
    actor: AdminUser,
    q: str | None = None,
    role: UserRole | None = None,
    is_active: bool | None = None,
    sort_by: str = Query(default="created_at"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    items, total = AdminUserService(db).list_users(
        actor,
        q=q,
        role=role,
        is_active=is_active,
        sort_by=sort_by,
        sort_dir=sort_dir,
        offset=(page - 1) * page_size,
        limit=page_size,
    )
    return paginate(total, page, page_size, [AdminUserOut.model_validate(u) for u in items])


@router.post("/users", response_model=AdminUserOut, status_code=201)
def create_admin_user(
    payload: AdminUserCreate,
    db: Annotated[Session, Depends(get_db)],
    actor: AdminUser,
):
    return AdminUserOut.model_validate(AdminUserService(db).create(actor, payload))


@router.get("/users/{user_id}", response_model=AdminUserOut)
def get_admin_user(user_id: UUID, db: Annotated[Session, Depends(get_db)], actor: AdminUser):
    return AdminUserOut.model_validate(AdminUserService(db).get(actor, user_id))


@router.patch("/users/{user_id}", response_model=AdminUserOut)
def update_admin_user(
    user_id: UUID,
    payload: AdminUserUpdate,
    db: Annotated[Session, Depends(get_db)],
    actor: AdminUser,
):
    return AdminUserOut.model_validate(AdminUserService(db).update(actor, user_id, payload))


@router.delete("/users/{user_id}")
def delete_admin_user(user_id: UUID, db: Annotated[Session, Depends(get_db)], actor: AdminUser):
    AdminUserService(db).delete(actor, user_id)
    return {"success": True, "message": "User deleted"}


@router.post("/users/{user_id}/suspend", response_model=AdminUserOut)
def suspend_user(user_id: UUID, db: Annotated[Session, Depends(get_db)], actor: AdminUser):
    return AdminUserOut.model_validate(AdminUserService(db).set_active(actor, user_id, False))


@router.post("/users/{user_id}/activate", response_model=AdminUserOut)
def activate_user(user_id: UUID, db: Annotated[Session, Depends(get_db)], actor: AdminUser):
    return AdminUserOut.model_validate(AdminUserService(db).set_active(actor, user_id, True))


@router.post("/users/{user_id}/reset-password", response_model=AdminUserOut)
def reset_user_password(
    user_id: UUID,
    payload: AdminPasswordReset,
    db: Annotated[Session, Depends(get_db)],
    actor: AdminUser,
):
    return AdminUserOut.model_validate(AdminUserService(db).reset_password(actor, user_id, payload))


@router.post("/users/{user_id}/avatar", response_model=AdminUserOut)
async def upload_user_avatar(
    user_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    actor: AdminUser,
    file: UploadFile = File(...),
):
    return AdminUserOut.model_validate(AdminUserService(db).upload_avatar(actor, user_id, file))


@router.get("/cases", response_model=PageOut[AdminCaseOut])
def list_admin_cases(
    db: Annotated[Session, Depends(get_db)],
    actor: AdminUser,
    q: str | None = None,
    status: CaseStatus | None = None,
    priority: CasePriority | None = None,
    sort_by: str = Query(default="updated_at"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    svc = AdminCaseService(db)
    items, total = svc.list(
        actor,
        q=q,
        status_filter=status,
        priority=priority,
        sort_by=sort_by,
        sort_dir=sort_dir,
        offset=(page - 1) * page_size,
        limit=page_size,
    )
    return paginate(total, page, page_size, [svc.to_out(c) for c in items])


@router.post("/cases", response_model=AdminCaseOut, status_code=201)
def create_admin_case(
    payload: AdminCaseCreate,
    db: Annotated[Session, Depends(get_db)],
    actor: AdminUser,
):
    svc = AdminCaseService(db)
    return svc.to_out(svc.create(actor, payload))


@router.get("/cases/{case_id}", response_model=AdminCaseOut)
def get_admin_case(case_id: UUID, db: Annotated[Session, Depends(get_db)], actor: AdminUser):
    svc = AdminCaseService(db)
    return svc.to_out(svc.get(actor, case_id))


@router.patch("/cases/{case_id}", response_model=AdminCaseOut)
def update_admin_case(
    case_id: UUID,
    payload: AdminCaseUpdate,
    db: Annotated[Session, Depends(get_db)],
    actor: AdminUser,
):
    svc = AdminCaseService(db)
    return svc.to_out(svc.update(actor, case_id, payload))


@router.delete("/cases/{case_id}")
def delete_admin_case(case_id: UUID, db: Annotated[Session, Depends(get_db)], actor: AdminUser):
    AdminCaseService(db).delete(actor, case_id)
    return {"success": True, "message": "Case deleted"}


@router.post("/cases/{case_id}/assign", response_model=AdminCaseOut)
def assign_admin_case(
    case_id: UUID,
    payload: AdminCaseAssign,
    db: Annotated[Session, Depends(get_db)],
    actor: AdminUser,
):
    svc = AdminCaseService(db)
    return svc.to_out(svc.assign(actor, case_id, payload))


@router.post("/cases/{case_id}/archive", response_model=AdminCaseOut)
def archive_admin_case(case_id: UUID, db: Annotated[Session, Depends(get_db)], actor: AdminUser):
    svc = AdminCaseService(db)
    return svc.to_out(svc.archive(actor, case_id))


@router.get("/evidence/storage", response_model=StorageUsageOut)
def evidence_storage(db: Annotated[Session, Depends(get_db)], actor: AdminUser):
    return AdminEvidenceService(db).storage_usage(actor)


@router.get("/evidence", response_model=PageOut[EvidenceAdminOut])
def list_admin_evidence(
    db: Annotated[Session, Depends(get_db)],
    actor: AdminUser,
    q: str | None = None,
    file_type: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    svc = AdminEvidenceService(db)
    items, total = svc.list(actor, q=q, file_type=file_type, offset=(page - 1) * page_size, limit=page_size)
    return paginate(total, page, page_size, [svc.to_out(i) for i in items])


@router.delete("/evidence/{evidence_id}")
def delete_admin_evidence(evidence_id: UUID, db: Annotated[Session, Depends(get_db)], actor: AdminUser):
    AdminEvidenceService(db).delete(actor, evidence_id)
    return {"success": True, "message": "Evidence deleted"}


@router.post("/reports/generate", response_model=AdminReportOut)
def generate_admin_report(
    payload: AdminReportRequest,
    db: Annotated[Session, Depends(get_db)],
    actor: AdminUser,
):
    return AdminReportService(db).generate(actor, payload)


@router.get("/reports", response_model=PageOut[ReportOut])
def list_admin_reports(
    db: Annotated[Session, Depends(get_db)],
    actor: AdminUser,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    items, total = AdminReportService(db).list_saved(actor, offset=(page - 1) * page_size, limit=page_size)
    return paginate(total, page, page_size, [ReportOut.model_validate(r) for r in items])


@router.get("/reports/export")
def export_generated_report(
    db: Annotated[Session, Depends(get_db)],
    actor: AdminUser,
    report_type: str = Query(..., pattern="^(case|department|investigator|evidence)$"),
    format: str = Query(default="csv", pattern="^(csv|pdf|html)$"),
    case_id: UUID | None = None,
    investigator_id: UUID | None = None,
):
    from app.models.enums import ReportFormat

    result = AdminReportService(db).generate(
        actor,
        AdminReportRequest(
            report_type=report_type,
            format=ReportFormat(format),
            case_id=case_id,
            investigator_id=investigator_id,
        ),
    )
    media = "text/csv" if result.format == ReportFormat.csv else "text/html"
    filename = f"{result.report_type}-report.{'csv' if result.format == ReportFormat.csv else 'html'}"
    return Response(
        content=result.content,
        media_type=media,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/activity", response_model=PageOut[ActivityOut])
def admin_module_activity(
    db: Annotated[Session, Depends(get_db)],
    actor: AdminUser,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
):
    from sqlalchemy import select
    from sqlalchemy.orm import joinedload

    from app.models.audit import ActivityLog
    from app.services.admin_scope import admin_department_id

    scope = admin_department_id(actor)
    stmt = select(ActivityLog).options(joinedload(ActivityLog.user))
    count_stmt = select(__import__("sqlalchemy").func.count()).select_from(ActivityLog)
    if scope is not None:
        stmt = stmt.join(User, User.id == ActivityLog.user_id).where(User.department_id == scope)
        count_stmt = count_stmt.join(User, User.id == ActivityLog.user_id).where(User.department_id == scope)
    total = db.scalar(count_stmt) or 0
    items = list(
        db.scalars(
            stmt.order_by(ActivityLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        )
        .unique()
        .all()
    )
    return paginate(total, page, page_size, [ActivityOut.model_validate(i) for i in items])
