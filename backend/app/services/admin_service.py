"""Admin module service — department-scoped users, cases, evidence, reports."""

from __future__ import annotations

import csv
import io
import secrets
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.security import hash_password
from app.models.audit import ActivityLog, Notification, Report
from app.models.case import Case, CaseAssignment, InvestigatorAssignment
from app.models.department import Department
from app.models.enums import (
    ActivityAction,
    CasePriority,
    CaseStatus,
    NotificationType,
    ReportFormat,
    TimelineEventType,
)
from app.models.evidence import Evidence
from app.models.note import Note
from app.models.timeline import TimelineEvent
from app.models.user import User, UserRole
from app.repositories.case_repository import CaseRepository
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
    InvestigatorAssignmentOut,
    StorageUsageOut,
)
from app.schemas.domain import ActivityOut, CaseAssignmentOut, NotificationOut, UserBrief
from app.services.activity import log_activity
from app.services.admin_scope import admin_department_id, assert_admin_creatable_role, assert_same_department
from app.services.notifications import notify
from app.services.storage import get_storage


class AdminUserService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_users(
        self,
        actor: User,
        *,
        q: str | None = None,
        role: UserRole | None = None,
        is_active: bool | None = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[User], int]:
        scope = admin_department_id(actor)
        stmt = select(User).where(User.role.notin_([UserRole.major_admin, UserRole.admin]))
        count_stmt = select(func.count()).select_from(User).where(
            User.role.notin_([UserRole.major_admin, UserRole.admin])
        )
        if scope is not None:
            stmt = stmt.where(User.department_id == scope)
            count_stmt = count_stmt.where(User.department_id == scope)
        if role:
            stmt = stmt.where(User.role == role)
            count_stmt = count_stmt.where(User.role == role)
        if is_active is not None:
            stmt = stmt.where(User.is_active.is_(is_active))
            count_stmt = count_stmt.where(User.is_active.is_(is_active))
        if q:
            like = f"%{q}%"
            filt = or_(
                User.full_name.ilike(like),
                User.email.ilike(like),
                User.badge_number.ilike(like),
                User.phone.ilike(like),
            )
            stmt = stmt.where(filt)
            count_stmt = count_stmt.where(filt)

        sort_col = {
            "created_at": User.created_at,
            "full_name": User.full_name,
            "email": User.email,
            "role": User.role,
            "last_login": User.last_login,
        }.get(sort_by, User.created_at)
        stmt = stmt.order_by(sort_col.desc() if sort_dir == "desc" else sort_col.asc())
        total = self.db.scalar(count_stmt) or 0
        items = list(self.db.scalars(stmt.offset(offset).limit(limit)).all())
        return items, total

    def get(self, actor: User, user_id: UUID) -> User:
        user = self.db.get(User, user_id)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
        assert_same_department(actor, user)
        return user

    def create(self, actor: User, payload: AdminUserCreate) -> User:
        assert_admin_creatable_role(payload.role)
        scope = admin_department_id(actor)

        email = payload.email.lower()
        if self.db.scalar(select(User).where(User.email == email)):
            raise HTTPException(status.HTTP_409_CONFLICT, detail="Email already registered")

        badge = payload.badge_number.strip() if payload.badge_number else None
        if badge and self.db.scalar(select(User).where(User.badge_number == badge)):
            raise HTTPException(status.HTTP_409_CONFLICT, detail="Badge number already in use")

        dept_id = scope
        dept_name = actor.department
        if scope is None and payload.department_id:
            dept = self.db.get(Department, payload.department_id)
            if not dept:
                raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Department not found")
            dept_id = dept.id
            dept_name = dept.name
        elif scope is not None:
            dept = self.db.get(Department, scope)
            dept_name = dept.name if dept else actor.department
        elif payload.department:
            dept_name = payload.department.strip()

        user = User(
            full_name=payload.full_name.strip(),
            email=email,
            password_hash=hash_password(payload.password),
            role=payload.role,
            department=dept_name,
            department_id=dept_id,
            phone=payload.phone.strip() if payload.phone else None,
            badge_number=badge,
            is_active=payload.is_active,
        )
        self.db.add(user)
        self.db.flush()

        notify(
            self.db,
            user_id=actor.id,
            notification_type=NotificationType.user_created,
            title="User created",
            message=f"{user.full_name} ({user.role.value}) was created",
            link="/admin/users",
        )
        log_activity(
            self.db,
            user_id=actor.id,
            action=ActivityAction.create,
            resource_type="user",
            resource_id=str(user.id),
            description=f"Created user {user.email}",
        )
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, actor: User, user_id: UUID, payload: AdminUserUpdate) -> User:
        user = self.get(actor, user_id)
        data = payload.model_dump(exclude_unset=True)
        if "role" in data and data["role"] is not None:
            assert_admin_creatable_role(data["role"])
        if "badge_number" in data and data["badge_number"]:
            badge = data["badge_number"].strip()
            existing = self.db.scalar(
                select(User).where(User.badge_number == badge, User.id != user.id)
            )
            if existing:
                raise HTTPException(status.HTTP_409_CONFLICT, detail="Badge number already in use")
            data["badge_number"] = badge
        for k, v in data.items():
            setattr(user, k, v)
        log_activity(
            self.db,
            user_id=actor.id,
            action=ActivityAction.update,
            resource_type="user",
            resource_id=str(user.id),
            description=f"Updated user {user.email}",
        )
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, actor: User, user_id: UUID) -> None:
        user = self.get(actor, user_id)
        email = user.email
        self.db.delete(user)
        log_activity(
            self.db,
            user_id=actor.id,
            action=ActivityAction.delete,
            resource_type="user",
            resource_id=str(user_id),
            description=f"Deleted user {email}",
        )
        self.db.commit()

    def set_active(self, actor: User, user_id: UUID, active: bool) -> User:
        user = self.get(actor, user_id)
        user.is_active = active
        log_activity(
            self.db,
            user_id=actor.id,
            action=ActivityAction.update,
            resource_type="user",
            resource_id=str(user.id),
            description=f"{'Activated' if active else 'Suspended'} user {user.email}",
        )
        self.db.commit()
        self.db.refresh(user)
        return user

    def reset_password(self, actor: User, user_id: UUID, payload: AdminPasswordReset) -> User:
        user = self.get(actor, user_id)
        user.password_hash = hash_password(payload.new_password)
        log_activity(
            self.db,
            user_id=actor.id,
            action=ActivityAction.password_reset,
            resource_type="user",
            resource_id=str(user.id),
            description=f"Reset password for {user.email}",
        )
        self.db.commit()
        self.db.refresh(user)
        return user

    def upload_avatar(self, actor: User, user_id: UUID, file: UploadFile) -> User:
        user = self.get(actor, user_id)
        data = file.file.read()
        if not data:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Empty file")
        if len(data) > 5 * 1024 * 1024:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Profile image must be ≤ 5MB")
        storage = get_storage()
        path, _ = storage.save(case_id=f"avatars/{user.id}", filename=file.filename or "avatar.jpg", data=data)
        user.profile_image_url = path
        self.db.commit()
        self.db.refresh(user)
        return user


class AdminCaseService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = CaseRepository(db)

    def _scope_filter(self, actor: User):
        return admin_department_id(actor)

    def _ensure_case_access(self, actor: User, case: Case) -> None:
        scope = self._scope_filter(actor)
        if scope is not None and case.department_id != scope:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Case is outside your department")

    def _validate_staff(self, actor: User, user_id: UUID, expected: UserRole) -> User:
        user = self.db.get(User, user_id)
        if not user or not user.is_active:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Assignee not found")
        if user.role != expected:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"User must be {expected.value}")
        assert_same_department(actor, user)
        return user

    def to_out(self, case: Case) -> AdminCaseOut:
        evidence_count = (
            self.db.scalar(select(func.count()).select_from(Evidence).where(Evidence.case_id == case.id)) or 0
        )
        notes_count = self.db.scalar(select(func.count()).select_from(Note).where(Note.case_id == case.id)) or 0
        timeline_count = (
            self.db.scalar(select(func.count()).select_from(TimelineEvent).where(TimelineEvent.case_id == case.id))
            or 0
        )
        superior = None
        for a in case.assignments or []:
            if a.is_primary and a.user:
                superior = UserBrief.model_validate(a.user)
                break
            if a.user and a.user.role == UserRole.superior_officer:
                superior = UserBrief.model_validate(a.user)
        investigators = [
            UserBrief.model_validate(a.user)
            for a in (case.investigator_assignments or [])
            if a.user
        ]
        base = AdminCaseOut(
            id=case.id,
            case_number=case.case_number,
            title=case.title,
            description=case.description,
            priority=case.priority,
            status=case.status,
            notes=case.notes,
            created_by_id=case.created_by_id,
            created_at=case.created_at,
            updated_at=case.updated_at,
            created_by=UserBrief.model_validate(case.created_by) if case.created_by else None,
            assignments=[CaseAssignmentOut.model_validate(a) for a in (case.assignments or [])],
            department_id=case.department_id,
            evidence_count=evidence_count,
            notes_count=notes_count,
            timeline_count=timeline_count,
            superior_officer=superior,
            investigators=investigators,
            investigator_assignments=[
                InvestigatorAssignmentOut.model_validate(a) for a in (case.investigator_assignments or [])
            ],
        )
        return base

    def list(
        self,
        actor: User,
        *,
        q: str | None = None,
        status_filter: CaseStatus | None = None,
        priority: CasePriority | None = None,
        sort_by: str = "updated_at",
        sort_dir: str = "desc",
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Case], int]:
        scope = self._scope_filter(actor)
        stmt = select(Case).options(
            selectinload(Case.assignments).joinedload(CaseAssignment.user),
            selectinload(Case.investigator_assignments).joinedload(InvestigatorAssignment.user),
            joinedload(Case.created_by),
        )
        count_stmt = select(func.count()).select_from(Case)
        if scope is not None:
            stmt = stmt.where(Case.department_id == scope)
            count_stmt = count_stmt.where(Case.department_id == scope)
        if q:
            like = f"%{q}%"
            filt = or_(Case.title.ilike(like), Case.case_number.ilike(like), Case.description.ilike(like))
            stmt = stmt.where(filt)
            count_stmt = count_stmt.where(filt)
        if status_filter:
            stmt = stmt.where(Case.status == status_filter)
            count_stmt = count_stmt.where(Case.status == status_filter)
        if priority:
            stmt = stmt.where(Case.priority == priority)
            count_stmt = count_stmt.where(Case.priority == priority)

        sort_col = {
            "created_at": Case.created_at,
            "updated_at": Case.updated_at,
            "title": Case.title,
            "priority": Case.priority,
            "status": Case.status,
            "case_number": Case.case_number,
        }.get(sort_by, Case.updated_at)
        stmt = stmt.order_by(sort_col.desc() if sort_dir == "desc" else sort_col.asc())
        total = self.db.scalar(count_stmt) or 0
        items = list(self.db.scalars(stmt.offset(offset).limit(limit)).unique().all())
        return items, total

    def get(self, actor: User, case_id: UUID) -> Case:
        case = self.repo.get(case_id)
        if not case:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Case not found")
        # Reload with investigator assignments
        case = self.db.scalar(
            select(Case)
            .options(
                selectinload(Case.assignments).joinedload(CaseAssignment.user),
                selectinload(Case.investigator_assignments).joinedload(InvestigatorAssignment.user),
                joinedload(Case.created_by),
            )
            .where(Case.id == case_id)
        )
        assert case is not None
        self._ensure_case_access(actor, case)
        return case

    def _apply_assignments(
        self,
        actor: User,
        case: Case,
        *,
        superior_officer_id: UUID | None,
        investigator_ids: list[UUID],
        replace_investigators: bool = False,
    ) -> None:
        if superior_officer_id:
            superior = self._validate_staff(actor, superior_officer_id, UserRole.superior_officer)
            # Clear other primary superiors; keep assignment row for superior
            for a in list(case.assignments):
                if a.user and a.user.role == UserRole.superior_officer:
                    self.db.delete(a)
            self.db.flush()
            self.db.add(
                CaseAssignment(
                    case_id=case.id,
                    user_id=superior.id,
                    assigned_by_id=actor.id,
                    is_primary=True,
                )
            )
            notify(
                self.db,
                user_id=superior.id,
                notification_type=NotificationType.case_assigned,
                title="Case assigned",
                message=f"You were assigned as Superior Officer on {case.case_number}",
                link=f"/admin/cases",
            )

        if replace_investigators:
            for a in list(case.investigator_assignments):
                self.db.delete(a)
            self.db.flush()

        for uid in investigator_ids:
            inv = self._validate_staff(actor, uid, UserRole.investigator)
            exists = next((a for a in case.investigator_assignments if a.user_id == uid), None)
            if exists and not replace_investigators:
                continue
            if not exists or replace_investigators:
                self.db.add(
                    InvestigatorAssignment(
                        case_id=case.id,
                        user_id=inv.id,
                        assigned_by_id=actor.id,
                    )
                )
                # Mirror into case_assignments for shared APIs
                if not any(a.user_id == inv.id for a in case.assignments):
                    self.db.add(
                        CaseAssignment(
                            case_id=case.id,
                            user_id=inv.id,
                            assigned_by_id=actor.id,
                            is_primary=False,
                        )
                    )
                notify(
                    self.db,
                    user_id=inv.id,
                    notification_type=NotificationType.case_assigned,
                    title="Case assigned",
                    message=f"You were assigned to case {case.case_number}",
                    link=f"/admin/cases",
                )
                self.db.add(
                    TimelineEvent(
                        case_id=case.id,
                        event_type=TimelineEventType.investigator_assigned,
                        title="Investigator assigned",
                        description=inv.full_name,
                        created_by_id=actor.id,
                    )
                )

    def create(self, actor: User, payload: AdminCaseCreate) -> Case:
        scope = self._scope_filter(actor)
        case = Case(
            case_number=self.repo.next_case_number(),
            title=payload.title.strip(),
            description=payload.description,
            priority=payload.priority,
            status=payload.status,
            notes=payload.notes,
            created_by_id=actor.id,
            department_id=scope or actor.department_id,
        )
        self.repo.add(case)
        self.db.flush()
        self.db.add(
            TimelineEvent(
                case_id=case.id,
                event_type=TimelineEventType.case_created,
                title="Case created",
                description=f"{case.case_number} — {case.title}",
                created_by_id=actor.id,
                event_at=datetime.now(timezone.utc),
            )
        )
        self._apply_assignments(
            actor,
            case,
            superior_officer_id=payload.superior_officer_id,
            investigator_ids=list(dict.fromkeys(payload.investigator_ids or [])),
            replace_investigators=True,
        )
        log_activity(
            self.db,
            user_id=actor.id,
            action=ActivityAction.create,
            resource_type="case",
            resource_id=str(case.id),
            description=f"Created case {case.case_number}",
        )
        self.db.commit()
        return self.get(actor, case.id)

    def update(self, actor: User, case_id: UUID, payload: AdminCaseUpdate) -> Case:
        case = self.get(actor, case_id)
        data = payload.model_dump(exclude_unset=True, exclude={"superior_officer_id", "investigator_ids"})
        status_changed = "status" in data and data["status"] != case.status
        old_status = case.status
        for k, v in data.items():
            setattr(case, k, v)
        case.updated_at = datetime.now(timezone.utc)

        if "superior_officer_id" in payload.model_fields_set or "investigator_ids" in payload.model_fields_set:
            self._apply_assignments(
                actor,
                case,
                superior_officer_id=payload.superior_officer_id,
                investigator_ids=list(dict.fromkeys(payload.investigator_ids or [])),
                replace_investigators="investigator_ids" in payload.model_fields_set,
            )

        if status_changed:
            self.db.add(
                TimelineEvent(
                    case_id=case.id,
                    event_type=TimelineEventType.status_updated,
                    title="Status updated",
                    description=f"{old_status.value} → {case.status.value}",
                    created_by_id=actor.id,
                )
            )
            if case.status in {CaseStatus.completed, CaseStatus.archived}:
                notify(
                    self.db,
                    user_id=actor.id,
                    notification_type=NotificationType.case_closed,
                    title="Case closed",
                    message=f"{case.case_number} is now {case.status.value}",
                    link="/admin/cases",
                )

        log_activity(
            self.db,
            user_id=actor.id,
            action=ActivityAction.update,
            resource_type="case",
            resource_id=str(case.id),
            description=f"Updated case {case.case_number}",
        )
        self.db.commit()
        return self.get(actor, case_id)

    def assign(self, actor: User, case_id: UUID, payload: AdminCaseAssign) -> Case:
        case = self.get(actor, case_id)
        self._apply_assignments(
            actor,
            case,
            superior_officer_id=payload.superior_officer_id,
            investigator_ids=list(dict.fromkeys(payload.investigator_ids or [])),
            replace_investigators=bool(payload.investigator_ids),
        )
        case.updated_at = datetime.now(timezone.utc)
        log_activity(
            self.db,
            user_id=actor.id,
            action=ActivityAction.update,
            resource_type="case",
            resource_id=str(case.id),
            description=f"Updated assignments for {case.case_number}",
        )
        self.db.commit()
        return self.get(actor, case_id)

    def archive(self, actor: User, case_id: UUID) -> Case:
        return self.update(actor, case_id, AdminCaseUpdate(status=CaseStatus.archived))

    def delete(self, actor: User, case_id: UUID) -> None:
        case = self.get(actor, case_id)
        number = case.case_number
        self.repo.delete(case)
        log_activity(
            self.db,
            user_id=actor.id,
            action=ActivityAction.delete,
            resource_type="case",
            resource_id=str(case_id),
            description=f"Deleted case {number}",
        )
        self.db.commit()


class AdminEvidenceService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(
        self,
        actor: User,
        *,
        q: str | None = None,
        file_type: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[Evidence], int]:
        scope = admin_department_id(actor)
        stmt = (
            select(Evidence)
            .join(Case, Case.id == Evidence.case_id)
            .options(joinedload(Evidence.uploaded_by), joinedload(Evidence.case))
        )
        count_stmt = select(func.count()).select_from(Evidence).join(Case, Case.id == Evidence.case_id)
        if scope is not None:
            stmt = stmt.where(Case.department_id == scope)
            count_stmt = count_stmt.where(Case.department_id == scope)
        if q:
            like = f"%{q}%"
            filt = or_(
                Evidence.original_name.ilike(like),
                Evidence.description.ilike(like),
                Case.case_number.ilike(like),
            )
            stmt = stmt.where(filt)
            count_stmt = count_stmt.where(filt)
        if file_type:
            stmt = stmt.where(Evidence.file_type == file_type)
            count_stmt = count_stmt.where(Evidence.file_type == file_type)
        total = self.db.scalar(count_stmt) or 0
        items = list(
            self.db.scalars(stmt.order_by(Evidence.upload_date.desc()).offset(offset).limit(limit)).unique().all()
        )
        return items, total

    def to_out(self, item: Evidence) -> EvidenceAdminOut:
        out = EvidenceAdminOut.model_validate(item)
        if item.case:
            out.case_number = item.case.case_number
        return out

    def delete(self, actor: User, evidence_id: UUID) -> None:
        item = self.db.get(Evidence, evidence_id)
        if not item:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Evidence not found")
        case = self.db.get(Case, item.case_id)
        if not case:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Case not found")
        scope = admin_department_id(actor)
        if scope is not None and case.department_id != scope:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Evidence outside your department")
        storage = get_storage()
        try:
            storage.delete(item.storage_path)
        except Exception:
            pass
        self.db.delete(item)
        log_activity(
            self.db,
            user_id=actor.id,
            action=ActivityAction.delete,
            resource_type="evidence",
            resource_id=str(evidence_id),
            description=f"Deleted evidence {item.original_name}",
        )
        self.db.commit()

    def storage_usage(self, actor: User) -> StorageUsageOut:
        scope = admin_department_id(actor)
        stmt = select(Evidence).join(Case, Case.id == Evidence.case_id)
        if scope is not None:
            stmt = stmt.where(Case.department_id == scope)
        items = list(self.db.scalars(stmt).all())
        by_type: dict[str, dict[str, int]] = {}
        total = 0
        for e in items:
            total += e.file_size or 0
            bucket = by_type.setdefault(e.file_type, {"type": e.file_type, "count": 0, "bytes": 0})
            bucket["count"] += 1
            bucket["bytes"] += e.file_size or 0
        return StorageUsageOut(total_files=len(items), total_bytes=total, by_type=list(by_type.values()))


class AdminReportService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.cases = AdminCaseService(db)
        self.evidence = AdminEvidenceService(db)
        self.users = AdminUserService(db)

    def generate(self, actor: User, payload: AdminReportRequest) -> AdminReportOut:
        if payload.report_type == "case":
            if not payload.case_id:
                raise HTTPException(400, detail="case_id required")
            case = self.cases.get(actor, payload.case_id)
            evidence, _ = self.evidence.list(actor, q=case.case_number, limit=500)
            summary = {
                "case_number": case.case_number,
                "title": case.title,
                "status": case.status.value,
                "priority": case.priority.value,
                "evidence_count": len(evidence),
            }
            title = payload.title or f"Case Report — {case.case_number}"
            content = self._render(payload.format, title, summary, evidence)
            report = Report(
                case_id=case.id,
                title=title,
                format=payload.format,
                content=content,
                generated_by_id=actor.id,
                summary_json=summary,
            )
            self.db.add(report)
            self.db.commit()
            self.db.refresh(report)
            return AdminReportOut(
                id=report.id,
                title=title,
                report_type="case",
                format=payload.format,
                content=content,
                created_at=report.created_at,
                summary=summary,
            )

        if payload.report_type == "department":
            cases, total = self.cases.list(actor, limit=500)
            users, utotal = self.users.list_users(actor, limit=500)
            summary = {
                "total_cases": total,
                "total_users": utotal,
                "open_cases": sum(1 for c in cases if c.status not in {CaseStatus.completed, CaseStatus.archived}),
                "closed_cases": sum(1 for c in cases if c.status in {CaseStatus.completed, CaseStatus.archived}),
            }
            title = payload.title or "Department Report"
            content = self._render(payload.format, title, summary, [])
            return AdminReportOut(
                title=title,
                report_type="department",
                format=payload.format,
                content=content,
                created_at=datetime.now(timezone.utc),
                summary=summary,
            )

        if payload.report_type == "investigator":
            if not payload.investigator_id:
                raise HTTPException(400, detail="investigator_id required")
            user = self.users.get(actor, payload.investigator_id)
            cases, _ = self.cases.list(actor, limit=500)
            assigned = [
                c
                for c in cases
                if any(a.user_id == user.id for a in (c.investigator_assignments or []))
                or any(a.user_id == user.id for a in (c.assignments or []))
            ]
            summary = {
                "investigator": user.full_name,
                "email": user.email,
                "assigned_cases": len(assigned),
                "cases": [c.case_number for c in assigned],
            }
            title = payload.title or f"Investigator Report — {user.full_name}"
            content = self._render(payload.format, title, summary, [])
            return AdminReportOut(
                title=title,
                report_type="investigator",
                format=payload.format,
                content=content,
                created_at=datetime.now(timezone.utc),
                summary=summary,
            )

        # evidence
        evidence, total = self.evidence.list(actor, limit=500)
        usage = self.evidence.storage_usage(actor)
        summary = {
            "total_files": total,
            "storage_bytes": usage.total_bytes,
            "by_type": usage.by_type,
        }
        title = payload.title or "Evidence Report"
        content = self._render(payload.format, title, summary, evidence)
        return AdminReportOut(
            title=title,
            report_type="evidence",
            format=payload.format,
            content=content,
            created_at=datetime.now(timezone.utc),
            summary=summary,
        )

    def _render(self, fmt: ReportFormat, title: str, summary: dict, evidence: list[Evidence]) -> str:
        if fmt == ReportFormat.csv:
            buf = io.StringIO()
            w = csv.writer(buf)
            w.writerow(["Field", "Value"])
            for k, v in summary.items():
                w.writerow([k, v])
            if evidence:
                w.writerow([])
                w.writerow(["Evidence", "Type", "Size", "SHA256", "Duplicate"])
                for e in evidence:
                    w.writerow([e.original_name, e.file_type, e.file_size, e.sha256_hash, e.is_duplicate])
            return buf.getvalue()
        lines = [f"<h1>{title}</h1>"]
        for k, v in summary.items():
            lines.append(f"<p><strong>{k}:</strong> {v}</p>")
        if evidence:
            lines.append("<h2>Evidence</h2><ul>")
            for e in evidence:
                dup = " (duplicate)" if e.is_duplicate else ""
                lines.append(f"<li>{e.original_name} — {e.file_type}{dup}</li>")
            lines.append("</ul>")
        return "\n".join(lines)

    def list_saved(self, actor: User, *, offset: int = 0, limit: int = 50) -> tuple[list[Report], int]:
        scope = admin_department_id(actor)
        stmt = select(Report).join(Case, Case.id == Report.case_id)
        count_stmt = select(func.count()).select_from(Report).join(Case, Case.id == Report.case_id)
        if scope is not None:
            stmt = stmt.where(Case.department_id == scope)
            count_stmt = count_stmt.where(Case.department_id == scope)
        total = self.db.scalar(count_stmt) or 0
        items = list(self.db.scalars(stmt.order_by(Report.created_at.desc()).offset(offset).limit(limit)).all())
        return items, total


class AdminDashboardService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.cases = AdminCaseService(db)
        self.users = AdminUserService(db)
        self.evidence = AdminEvidenceService(db)

    def stats(self, actor: User) -> AdminDashboardStats:
        scope = admin_department_id(actor)

        def count_users(role: UserRole) -> int:
            stmt = select(func.count()).select_from(User).where(User.role == role)
            if scope is not None:
                stmt = stmt.where(User.department_id == scope)
            return self.db.scalar(stmt) or 0

        case_filter = []
        if scope is not None:
            case_filter.append(Case.department_id == scope)

        total_cases = self.db.scalar(select(func.count()).select_from(Case).where(*case_filter)) or 0
        open_cases = (
            self.db.scalar(
                select(func.count())
                .select_from(Case)
                .where(*case_filter, Case.status.notin_([CaseStatus.completed, CaseStatus.archived]))
            )
            or 0
        )
        closed_cases = (
            self.db.scalar(
                select(func.count())
                .select_from(Case)
                .where(*case_filter, Case.status.in_([CaseStatus.completed, CaseStatus.archived]))
            )
            or 0
        )

        evid_stmt = select(func.count()).select_from(Evidence).join(Case, Case.id == Evidence.case_id)
        if scope is not None:
            evid_stmt = evid_stmt.where(Case.department_id == scope)
        evidence_count = self.db.scalar(evid_stmt) or 0

        monthly_q = (
            select(func.to_char(Case.created_at, "YYYY-MM").label("month"), func.count().label("count"))
            .group_by("month")
            .order_by("month")
            .limit(12)
        )
        if scope is not None:
            monthly_q = monthly_q.where(Case.department_id == scope)
        monthly_cases = [{"month": r.month, "count": r.count} for r in self.db.execute(monthly_q).all()]

        type_q = (
            select(Evidence.file_type, func.count())
            .join(Case, Case.id == Evidence.case_id)
            .group_by(Evidence.file_type)
        )
        if scope is not None:
            type_q = type_q.where(Case.department_id == scope)
        evidence_types = [{"type": r[0], "count": r[1]} for r in self.db.execute(type_q).all()]

        pri_q = select(Case.priority, func.count()).group_by(Case.priority)
        if scope is not None:
            pri_q = pri_q.where(Case.department_id == scope)
        priority_distribution = [
            {"priority": r[0].value if r[0] else "unknown", "count": r[1]} for r in self.db.execute(pri_q).all()
        ]

        # Department-scoped activity: actions by users in dept
        act_stmt = select(ActivityLog).options(joinedload(ActivityLog.user)).order_by(ActivityLog.created_at.desc())
        if scope is not None:
            act_stmt = act_stmt.join(User, User.id == ActivityLog.user_id).where(User.department_id == scope)
        activities = list(self.db.scalars(act_stmt.limit(10)).unique().all())

        recent_cases, _ = self.cases.list(actor, limit=5)
        notifications = list(
            self.db.scalars(
                select(Notification)
                .where(Notification.user_id == actor.id)
                .order_by(Notification.created_at.desc())
                .limit(10)
            ).all()
        )
        usage = self.evidence.storage_usage(actor)

        return AdminDashboardStats(
            superior_officers=count_users(UserRole.superior_officer),
            investigators=count_users(UserRole.investigator),
            total_cases=total_cases,
            open_cases=open_cases,
            closed_cases=closed_cases,
            evidence_count=evidence_count,
            monthly_cases=monthly_cases,
            evidence_types=evidence_types,
            priority_distribution=priority_distribution,
            recent_activity=[ActivityOut.model_validate(a) for a in activities],
            recent_cases=[self.cases.to_out(c) for c in recent_cases],
            notifications=[NotificationOut.model_validate(n) for n in notifications],
            storage_bytes=usage.total_bytes,
        )


def random_temp_password() -> str:
    return f"Tmp{secrets.token_hex(4)}1"
