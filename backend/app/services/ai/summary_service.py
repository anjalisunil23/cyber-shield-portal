"""AI-Assisted Case Investigation Summary Generator with Explicit Human-Verification Demarcation."""

from __future__ import annotations

import datetime
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.case import Case
from app.models.evidence import Evidence
from app.models.lead import ManualLead
from app.models.relationship import Relationship
from app.models.timeline import TimelineEvent


class SummaryService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def generate_case_summary(self, case_id: UUID) -> dict[str, Any]:
        """
        Generate comprehensive, structured investigation summary.
        Explicitly distinguishes AI recommendations from investigator-verified facts.
        """
        case = self.db.get(Case, case_id)
        if not case:
            from fastapi import HTTPException
            raise HTTPException(404, detail="Case not found")

        evidence_items = (
            self.db.query(Evidence)
            .filter(Evidence.case_id == case_id)
            .all()
        )

        relationships = (
            self.db.query(Relationship)
            .filter(Relationship.case_id == case_id)
            .all()
        )

        timeline_events = (
            self.db.query(TimelineEvent)
            .filter(TimelineEvent.case_id == case_id)
            .order_by(TimelineEvent.event_at.asc())
            .all()
        )

        leads = (
            self.db.query(ManualLead)
            .filter(ManualLead.case_id == case_id)
            .all()
        )

        # 1. Evidence Breakdown
        ev_summary = []
        for e in evidence_items:
            ev_summary.append({
                "id": str(e.id),
                "name": e.original_name,
                "file_type": e.file_type,
                "size_kb": round(e.file_size / 1024, 1),
                "sha256": e.sha256_hash,
                "is_duplicate": e.is_duplicate,
                "has_ocr": bool(e.ocr_text),
                "has_transcript": bool(e.speech_transcript),
            })

        # 2. Key Entities
        entities_list = []
        for e in evidence_items:
            ents = []
            if isinstance(e.extracted_entities, list):
                ents = e.extracted_entities
            elif isinstance(e.extracted_entities, dict) and "entities" in e.extracted_entities:
                ents = e.extracted_entities["entities"]
            for ent in ents[:10]:
                entities_list.append({
                    "type": ent.get("type", "ENTITY"),
                    "value": ent.get("normalized_value", ent.get("raw_value", "")),
                    "source_evidence": e.original_name,
                    "confidence": ent.get("confidence", 0.9),
                })

        # 3. Relationships & Verification Status
        rel_summary = []
        for r in relationships:
            rel_summary.append({
                "source": r.source_label,
                "target": r.target_label,
                "type": r.relationship_type.value,
                "description": r.description,
                "confidence": r.confidence or 0.85,
                "status": "AI-Generated (Decision Support)" if r.ai_generated else "Human Verified",
            })

        # 4. Leads Categorization (Verified vs Pending vs Rejected)
        verified_leads = []
        pending_leads = []
        rejected_leads = []

        for l in leads:
            meta = l.metadata_json or {}
            rev_state = meta.get("human_review_state", "PENDING_REVIEW")
            lead_obj = {
                "id": str(l.id),
                "title": l.title,
                "priority": l.priority.value,
                "status": l.status.value,
                "review_state": rev_state,
                "why": meta.get("why_explanation", l.justification or ""),
                "reviewer_note": l.review_comment or "No reviewer comments.",
            }
            if rev_state == "VERIFIED" or l.status.value == "approved":
                verified_leads.append(lead_obj)
            elif rev_state == "REJECTED" or l.status.value == "rejected":
                rejected_leads.append(lead_obj)
            else:
                pending_leads.append(lead_obj)

        now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        summary_data = {
            "case_id": str(case.id),
            "case_number": case.case_number,
            "title": case.title,
            "priority": case.priority.value,
            "status": case.status.value,
            "generated_at": now_str,
            "lead_investigator": case.investigator_lead.full_name if case.investigator_lead else "Unassigned",
            "supervisor": case.supervisor.full_name if case.supervisor else "Unassigned",
            "evidence_count": len(evidence_items),
            "evidence_summary": ev_summary,
            "important_entities": entities_list[:25],
            "key_relationships": rel_summary,
            "timeline_event_count": len(timeline_events),
            "timeline_events": [
                {
                    "time": t.event_at.strftime("%Y-%m-%d %H:%M") if t.event_at else "Unknown",
                    "title": t.title,
                    "description": t.description or "",
                }
                for t in timeline_events[:15]
            ],
            "verified_findings": verified_leads,
            "unverified_ai_leads": pending_leads,
            "rejected_leads": rejected_leads,
            "summary_text": (
                f"Investigation Case {case.case_number} ({case.title}) currently has {len(evidence_items)} digital evidence items ingested. "
                f"Multi-source correlation identified {len(relationships)} cross-evidence relationships. "
                f"There are {len(verified_leads)} officer-verified leads, {len(pending_leads)} unverified AI recommendations pending review, "
                f"and {len(rejected_leads)} dismissed findings."
            ),
            "summary": (
                f"Investigation Case {case.case_number} ({case.title}) currently has {len(evidence_items)} digital evidence items ingested. "
                f"Multi-source correlation identified {len(relationships)} cross-evidence relationships. "
                f"There are {len(verified_leads)} officer-verified leads, {len(pending_leads)} unverified AI recommendations pending review, "
                f"and {len(rejected_leads)} dismissed findings."
            ),
            "key_findings": [
                f"{len(evidence_items)} digital evidence files processed across EXIF, OCR, speech, and CDR modalities.",
                f"{len(relationships)} multi-hop cross-source entity correlations identified.",
                f"{len(verified_leads)} officer-verified actionable leads established.",
                f"{len(pending_leads)} AI-suggested leads pending human verification.",
            ],
            "disclaimer": (
                "Cyber Shield is an investigation support and decision-assistance platform. "
                "AI-generated findings are recommendations only and must be independently verified by authorized investigators."
            ),
        }

        return summary_data
