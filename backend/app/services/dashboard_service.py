"""Notes, timeline, relationships, leads, reports, search, dashboard services."""

from __future__ import annotations

import csv
import io
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.audit import Report
from app.models.case import Case
from app.models.enums import (
    ActivityAction,
    CasePriority,
    CaseStatus,
    NotificationType,
    ReportFormat,
    TimelineEventType,
)
from app.models.evidence import Evidence
from app.models.lead import ManualLead
from app.models.note import Note
from app.models.relationship import Relationship
from app.models.timeline import TimelineEvent
from app.models.user import User
from app.repositories.case_repository import CaseRepository
from app.repositories.common import (
    ActivityRepository,
    LeadRepository,
    NoteRepository,
    RelationshipRepository,
    ReportRepository,
    TimelineRepository,
    UserRepository,
)
from app.repositories.evidence_repository import EvidenceRepository
from app.schemas.domain import (
    DashboardStats,
    LeadCreate,
    LeadUpdate,
    NoteCreate,
    NoteUpdate,
    RelationshipCreate,
    ReportCreate,
    SearchResult,
    TimelineCreate,
)
from app.services.activity import log_activity
from app.services.notifications import notify


class NoteService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = NoteRepository(db)

    def create(self, case_id: UUID, payload: NoteCreate, actor: User) -> Note:
        if not self.db.get(Case, case_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Case not found")
        note = Note(
            case_id=case_id,
            author_id=actor.id,
            title=payload.title,
            body=payload.body,
            is_pinned=payload.is_pinned,
        )
        self.db.add(note)
        self.db.add(
            TimelineEvent(
                case_id=case_id,
                event_type=TimelineEventType.note_added,
                title="Note added",
                description=payload.title or payload.body[:80],
                created_by_id=actor.id,
            )
        )
        case = self.db.get(Case, case_id)
        if case:
            for a in case.assignments:
                if a.user_id != actor.id:
                    notify(
                        self.db,
                        user_id=a.user_id,
                        notification_type=NotificationType.new_note,
                        title="New note",
                        message=f"Note added on {case.case_number}",
                        link=f"/dashboard/cases/{case_id}",
                    )
        log_activity(
            self.db,
            user_id=actor.id,
            action=ActivityAction.create,
            resource_type="note",
            description="Created note",
        )
        self.db.commit()
        self.db.refresh(note)
        return self.repo.get(note.id)  # type: ignore[return-value]

    def update(self, note_id: UUID, payload: NoteUpdate, actor: User) -> Note:
        note = self.repo.get(note_id)
        if not note:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Note not found")
        for k, v in payload.model_dump(exclude_unset=True).items():
            setattr(note, k, v)
        note.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        return self.repo.get(note_id)  # type: ignore[return-value]

    def delete(self, note_id: UUID, actor: User) -> None:
        note = self.repo.get(note_id)
        if not note:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Note not found")
        self.db.delete(note)
        log_activity(
            self.db,
            user_id=actor.id,
            action=ActivityAction.delete,
            resource_type="note",
            resource_id=str(note_id),
            description="Deleted note",
        )
        self.db.commit()


class TimelineService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = TimelineRepository(db)

    def create(self, case_id: UUID, payload: TimelineCreate, actor: User) -> TimelineEvent:
        if not self.db.get(Case, case_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Case not found")
        event = TimelineEvent(
            case_id=case_id,
            event_type=payload.event_type,
            title=payload.title,
            description=payload.description,
            event_at=payload.event_at or datetime.now(timezone.utc),
            created_by_id=actor.id,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def delete(self, event_id: UUID) -> None:
        event = self.repo.get(event_id)
        if not event:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Event not found")
        self.db.delete(event)
        self.db.commit()


class RelationshipService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = RelationshipRepository(db)

    def create(self, case_id: UUID, payload: RelationshipCreate, actor: User) -> Relationship:
        if not self.db.get(Case, case_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Case not found")
        rel = Relationship(
            case_id=case_id,
            relationship_type=payload.relationship_type,
            source_kind=payload.source_kind,
            source_id=payload.source_id,
            source_label=payload.source_label,
            target_kind=payload.target_kind,
            target_id=payload.target_id,
            target_label=payload.target_label,
            description=payload.description,
            created_by_id=actor.id,
            ai_generated=False,
        )
        self.db.add(rel)
        self.db.add(
            TimelineEvent(
                case_id=case_id,
                event_type=TimelineEventType.relationship_created,
                title="Relationship created",
                description=f"{payload.source_label} → {payload.target_label}",
                created_by_id=actor.id,
            )
        )
        self.db.commit()
        self.db.refresh(rel)
        return rel

    def delete(self, rel_id: UUID) -> None:
        rel = self.repo.get(rel_id)
        if not rel:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Relationship not found")
        self.db.delete(rel)
        self.db.commit()


class LeadService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = LeadRepository(db)

    def create(self, case_id: UUID, payload: LeadCreate, actor: User) -> ManualLead:
        if not self.db.get(Case, case_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Case not found")
        lead = ManualLead(
            case_id=case_id,
            title=payload.title,
            description=payload.description,
            priority=payload.priority,
            status=payload.status,
            related_evidence_id=payload.related_evidence_id,
            assigned_to_id=payload.assigned_to_id,
            created_by_id=actor.id,
        )
        self.db.add(lead)
        self.db.add(
            TimelineEvent(
                case_id=case_id,
                event_type=TimelineEventType.lead_created,
                title="Lead created",
                description=payload.title,
                created_by_id=actor.id,
            )
        )
        if payload.assigned_to_id:
            notify(
                self.db,
                user_id=payload.assigned_to_id,
                notification_type=NotificationType.lead_created,
                title="Lead assigned",
                message=payload.title,
                link=f"/dashboard/cases/{case_id}",
            )
        self.db.commit()
        self.db.refresh(lead)
        return self.repo.get(lead.id)  # type: ignore[return-value]

    def update(self, lead_id: UUID, payload: LeadUpdate) -> ManualLead:
        lead = self.repo.get(lead_id)
        if not lead:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Lead not found")
        for k, v in payload.model_dump(exclude_unset=True).items():
            setattr(lead, k, v)
        lead.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        return self.repo.get(lead_id)  # type: ignore[return-value]

    def delete(self, lead_id: UUID) -> None:
        lead = self.repo.get(lead_id)
        if not lead:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Lead not found")
        self.db.delete(lead)
        self.db.commit()


class ReportService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ReportRepository(db)
        self.cases = CaseRepository(db)
        self.evidence = EvidenceRepository(db)
        self.notes = NoteRepository(db)

    def generate(self, case_id: UUID, payload: ReportCreate, actor: User) -> Report:
        case = self.cases.get(case_id)
        if not case:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Case not found")

        evidence, evid_count = self.evidence.list_for_case(case_id, limit=500)
        notes = self.notes.list_for_case(case_id)
        assignees = [a.user.full_name for a in case.assignments if a.user]

        summary = {
            "case_number": case.case_number,
            "title": case.title,
            "status": case.status.value,
            "priority": case.priority.value,
            "evidence_count": evid_count,
            "notes_count": len(notes),
            "assignees": assignees,
        }

        title = payload.title or f"Investigation Summary — {case.case_number}"
        content: str | None = None

        if payload.format == ReportFormat.csv:
            buf = io.StringIO()
            writer = csv.writer(buf)
            writer.writerow(["Field", "Value"])
            for k, v in summary.items():
                writer.writerow([k, v])
            writer.writerow([])
            writer.writerow(["Evidence", "Type", "Size", "SHA256"])
            for e in evidence:
                writer.writerow([e.original_name, e.file_type, e.file_size, e.sha256_hash])
            content = buf.getvalue()
        else:
            # HTML / print-friendly (also used as PDF source for browser print)
            lines = [
                f"<h1>{title}</h1>",
                f"<p><strong>Case:</strong> {case.case_number}</p>",
                f"<p><strong>Status:</strong> {case.status.value} | <strong>Priority:</strong> {case.priority.value}</p>",
                f"<p>{case.description or ''}</p>",
                f"<h2>Assignees</h2><ul>{''.join(f'<li>{n}</li>' for n in assignees)}</ul>",
                f"<h2>Evidence ({evid_count})</h2><ul>",
            ]
            for e in evidence:
                lines.append(f"<li>{e.original_name} ({e.file_type}, {e.file_size} bytes)</li>")
            lines.append("</ul><h2>Notes</h2>")
            for n in notes:
                lines.append(f"<div><strong>{n.title or 'Note'}</strong><pre>{n.body}</pre></div>")
            content = "\n".join(lines)

        report = Report(
            case_id=case_id,
            title=title,
            format=payload.format,
            content=content,
            generated_by_id=actor.id,
            summary_json=summary,
        )
        self.db.add(report)
        self.db.add(
            TimelineEvent(
                case_id=case_id,
                event_type=TimelineEventType.report_generated,
                title="Report generated",
                description=title,
                created_by_id=actor.id,
            )
        )
        log_activity(
            self.db,
            user_id=actor.id,
            action=ActivityAction.export,
            resource_type="report",
            description=f"Generated report for {case.case_number}",
        )
        self.db.commit()
        self.db.refresh(report)
        return report


class SearchService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def search(self, q: str) -> SearchResult:
        from app.schemas.domain import CaseOut, EvidenceOut, NoteOut, ReportOut, UserBrief

        if not q.strip():
            return SearchResult()
        cases, _ = CaseRepository(self.db).list(q=q, limit=10)
        evidence = EvidenceRepository(self.db).global_search(q, limit=10)
        notes = NoteRepository(self.db).search(q, limit=10)
        users = UserRepository(self.db).search(q, limit=10)
        reports = ReportRepository(self.db).search(q, limit=10)
        return SearchResult(
            cases=[CaseOut.model_validate(c) for c in cases],
            evidence=[EvidenceOut.model_validate(e) for e in evidence],
            notes=[NoteOut.model_validate(n) for n in notes],
            investigators=[UserBrief.model_validate(u) for u in users],
            reports=[ReportOut.model_validate(r) for r in reports],
        )


class DashboardService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def stats(self) -> DashboardStats:
        from app.schemas.domain import ActivityOut, CaseOut, EvidenceOut

        active = (
            self.db.scalar(
                select(func.count()).select_from(Case).where(
                    Case.status.notin_([CaseStatus.completed, CaseStatus.archived])
                )
            )
            or 0
        )
        completed = (
            self.db.scalar(select(func.count()).select_from(Case).where(Case.status == CaseStatus.completed))
            or 0
        )
        evidence_count = self.db.scalar(select(func.count()).select_from(Evidence)) or 0
        investigators = self.db.scalar(select(func.count()).select_from(User).where(User.is_active.is_(True))) or 0
        reports = self.db.scalar(select(func.count()).select_from(Report)) or 0

        # Monthly cases (last 6 months)
        monthly_raw = self.db.execute(
            select(
                func.to_char(Case.created_at, "YYYY-MM").label("month"),
                func.count().label("count"),
            )
            .group_by("month")
            .order_by("month")
            .limit(12)
        ).all()
        monthly_cases = [{"month": r.month, "count": r.count} for r in monthly_raw]

        type_raw = self.db.execute(
            select(Evidence.file_type, func.count()).group_by(Evidence.file_type)
        ).all()
        evidence_types = [{"type": r[0], "count": r[1]} for r in type_raw]

        pri_raw = self.db.execute(
            select(Case.priority, func.count()).group_by(Case.priority)
        ).all()
        priority_distribution = [{"priority": r[0].value if r[0] else "unknown", "count": r[1]} for r in pri_raw]

        activities, _ = ActivityRepository(self.db).list(limit=10)
        recent_cases, _ = CaseRepository(self.db).list(sort_by="created_at", sort_dir="desc", limit=5)
        latest = list(
            self.db.scalars(
                select(Evidence).order_by(Evidence.upload_date.desc()).limit(5)
            ).all()
        )

        return DashboardStats(
            active_cases=active,
            completed_cases=completed,
            evidence_uploaded=evidence_count,
            investigators=investigators,
            reports=reports,
            monthly_cases=monthly_cases,
            evidence_types=evidence_types,
            priority_distribution=priority_distribution,
            recent_activity=[ActivityOut.model_validate(a) for a in activities],
            recent_cases=[CaseOut.model_validate(c) for c in recent_cases],
            latest_uploads=[EvidenceOut.model_validate(e) for e in latest],
        )
