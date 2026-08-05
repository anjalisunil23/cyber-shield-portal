"""Case domain service."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.case import Case, CaseAssignment
from app.models.enums import ActivityAction, CasePriority, CaseStatus, NotificationType, TimelineEventType
from app.models.timeline import TimelineEvent
from app.models.user import User
from app.repositories.case_repository import CaseRepository
from app.schemas.domain import CaseAssign, CaseCreate, CaseUpdate
from app.services.activity import log_activity
from app.services.notifications import notify


class CaseService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = CaseRepository(db)

    def create(self, payload: CaseCreate, actor: User) -> Case:
        case = Case(
            case_number=self.repo.next_case_number(),
            title=payload.title.strip(),
            description=payload.description,
            priority=payload.priority,
            status=payload.status,
            notes=payload.notes,
            created_by_id=actor.id,
            department_id=getattr(actor, "department_id", None),
        )
        self.repo.add(case)
        self.db.flush()

        assignee_ids = list(dict.fromkeys(payload.assignee_ids or []))
        if actor.id not in assignee_ids:
            assignee_ids.insert(0, actor.id)

        for i, uid in enumerate(assignee_ids):
            self.db.add(
                CaseAssignment(
                    case_id=case.id,
                    user_id=uid,
                    assigned_by_id=actor.id,
                    is_primary=i == 0,
                )
            )
            if uid != actor.id:
                notify(
                    self.db,
                    user_id=uid,
                    notification_type=NotificationType.case_assigned,
                    title="Case assigned",
                    message=f"You were assigned to case {case.case_number}: {case.title}",
                    link=f"/dashboard/cases/{case.id}",
                )

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
        log_activity(
            self.db,
            user_id=actor.id,
            action=ActivityAction.create,
            resource_type="case",
            resource_id=str(case.id),
            description=f"Created case {case.case_number}",
        )
        self.db.commit()
        return self.repo.get(case.id)  # type: ignore[return-value]

    def update(self, case_id: UUID, payload: CaseUpdate, actor: User) -> Case:
        case = self.repo.get(case_id)
        if not case:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Case not found")

        data = payload.model_dump(exclude_unset=True)
        status_changed = "status" in data and data["status"] != case.status
        old_status = case.status

        for k, v in data.items():
            setattr(case, k, v)
        case.updated_at = datetime.now(timezone.utc)

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
            for a in case.assignments:
                if a.user_id != actor.id:
                    notify(
                        self.db,
                        user_id=a.user_id,
                        notification_type=NotificationType.status_changed,
                        title="Case status changed",
                        message=f"{case.case_number} is now {case.status.value}",
                        link=f"/dashboard/cases/{case.id}",
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
        return self.repo.get(case_id)  # type: ignore[return-value]

    def delete(self, case_id: UUID, actor: User) -> None:
        case = self.repo.get(case_id)
        if not case:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Case not found")
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

    def assign(self, case_id: UUID, payload: CaseAssign, actor: User) -> Case:
        case = self.repo.get(case_id)
        if not case:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Case not found")
        user = self.db.get(User, payload.user_id)
        if not user or not user.is_active:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

        existing = next((a for a in case.assignments if a.user_id == payload.user_id), None)
        if existing:
            existing.is_primary = payload.is_primary or existing.is_primary
        else:
            self.db.add(
                CaseAssignment(
                    case_id=case.id,
                    user_id=payload.user_id,
                    assigned_by_id=actor.id,
                    is_primary=payload.is_primary,
                )
            )
            notify(
                self.db,
                user_id=payload.user_id,
                notification_type=NotificationType.case_assigned,
                title="Case assigned",
                message=f"You were assigned to case {case.case_number}",
                link=f"/dashboard/cases/{case.id}",
            )

        self.db.add(
            TimelineEvent(
                case_id=case.id,
                event_type=TimelineEventType.investigator_assigned,
                title="Investigator assigned",
                description=user.full_name,
                created_by_id=actor.id,
            )
        )
        case.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        return self.repo.get(case_id)  # type: ignore[return-value]

    def list(
        self,
        *,
        q: str | None,
        status: CaseStatus | None,
        priority: CasePriority | None,
        assigned_to: UUID | None,
        sort_by: str,
        sort_dir: str,
        page: int,
        page_size: int,
    ) -> tuple[list[Case], int]:
        offset = (page - 1) * page_size
        return self.repo.list(
            q=q,
            status=status,
            priority=priority,
            assigned_to=assigned_to,
            sort_by=sort_by,
            sort_dir=sort_dir,
            offset=offset,
            limit=page_size,
        )

    def get(self, case_id: UUID) -> Case:
        case = self.repo.get(case_id)
        if not case:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Case not found")
        return case
