"""Explainable Investigative Lead Generation and Human Oversight Review Workflow."""

from __future__ import annotations

import datetime
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.enums import LeadPriority, LeadStatus
from app.models.lead import ManualLead
from app.models.user import User
from app.services.ai.risk_service import RiskService


class LeadServiceAI:
    def __init__(self, db: Session) -> None:
        self.db = db

    def generate_explainable_leads(
        self,
        case_id: UUID,
        correlations: list[dict[str, Any]],
        risk_assessment: dict[str, Any],
        actor_id: UUID,
    ) -> list[ManualLead]:
        """
        Synthesize explainable investigative leads from high-confidence cross-source correlations
        and risk indicators.
        """
        generated_leads: list[ManualLead] = []

        for corr in correlations:
            ent_type = corr["entity_type"]
            norm_val = corr["normalized_value"]
            evidence_ids = corr["supporting_evidence_ids"]
            ev_names = corr.get("supporting_evidence_names", [])
            conf = corr["confidence_score"]

            title = f"Cross-Source Correlation: {ent_type} '{norm_val}' detected across {len(evidence_ids)} files"
            description = (
                f"Identified entity {norm_val} recurring across multiple digital evidence items: "
                f"{', '.join(ev_names)}. High investigative priority for subject identification."
            )

            # Factors relevant to this lead
            lead_factors = [
                {"factor": "Multi-Source Recurrence", "points": 15},
                {"factor": "Cross-Evidence Alignment", "points": 20},
                {"factor": f"High Confidence Entity Match ({int(conf * 100)}%)", "points": 10},
            ]

            metadata_json = {
                "ai_generated": True,
                "confidence_score": conf,
                "confidence_pct": f"{int(conf * 100)}%",
                "risk_score": risk_assessment["risk_score"],
                "risk_level": risk_assessment["risk_level"],
                "why_explanation": corr["explanation"],
                "factors": lead_factors,
                "supporting_evidence_ids": evidence_ids,
                "supporting_evidence_names": ev_names,
                "human_review_state": "PENDING_REVIEW",
                "original_ai_recommendation": {
                    "title": title,
                    "description": description,
                    "priority": "high",
                },
            }

            # Check if this lead already exists to avoid duplicates
            existing = (
                self.db.query(ManualLead)
                .filter(
                    ManualLead.case_id == case_id,
                    ManualLead.title == title,
                )
                .first()
            )

            if not existing:
                lead = ManualLead(
                    case_id=case_id,
                    title=title,
                    description=description,
                    priority=LeadPriority.high,
                    status=LeadStatus.open,
                    related_evidence_ids=evidence_ids,
                    justification=corr["explanation"],
                    created_by_id=actor_id,
                    metadata_json=metadata_json,
                )
                self.db.add(lead)
                generated_leads.append(lead)
            else:
                existing.metadata_json = metadata_json
                generated_leads.append(existing)

        self.db.commit()
        return generated_leads

    def review_lead(
        self,
        lead_id: UUID,
        action: str,  # "verify", "reject", "modify"
        actor: User,
        modification_title: str | None = None,
        modification_description: str | None = None,
        reason: str | None = None,
    ) -> ManualLead:
        """
        Record investigator oversight decision (Verify, Reject, or Modify).
        Preserves original AI output and adds investigator audit record.
        """
        lead = self.db.get(ManualLead, lead_id)
        if not lead:
            from fastapi import HTTPException
            raise HTTPException(404, detail="Lead not found")

        meta = lead.metadata_json or {}
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        history = list(meta.get("review_history_log") or [])
        if isinstance(meta.get("review_history"), dict):
            history.append(meta["review_history"])

        if action == "verify":
            lead.status = LeadStatus.approved
            meta["human_review_state"] = "VERIFIED"
            review_record = {
                "action": "VERIFIED",
                "reviewer_id": str(actor.id),
                "reviewer_name": actor.full_name,
                "timestamp": now_iso,
                "reason": reason or "Confirmed by investigator after evidence review.",
            }
            meta["review_history"] = review_record
            history.append(review_record)
            lead.review_comment = f"VERIFIED by {actor.full_name}: {reason or 'Evidence verified.'}"

        elif action == "reject":
            lead.status = LeadStatus.rejected
            meta["human_review_state"] = "REJECTED"
            review_record = {
                "action": "REJECTED",
                "reviewer_id": str(actor.id),
                "reviewer_name": actor.full_name,
                "timestamp": now_iso,
                "reason": reason or "Investigator rejected lead after contextual analysis.",
            }
            meta["review_history"] = review_record
            history.append(review_record)
            lead.review_comment = f"REJECTED by {actor.full_name}: {reason or 'Deemed non-relevant.'}"

        elif action == "modify":
            lead.status = LeadStatus.in_progress
            meta["human_review_state"] = "MODIFIED"
            review_record = {
                "action": "MODIFIED",
                "reviewer_id": str(actor.id),
                "reviewer_name": actor.full_name,
                "timestamp": now_iso,
                "reason": reason or "Lead modified to incorporate investigator domain context.",
                "previous_title": lead.title,
                "previous_description": lead.description,
            }
            meta["review_history"] = review_record
            meta["modification_history"] = review_record
            history.append(review_record)
            if modification_title:
                lead.title = modification_title
            if modification_description:
                lead.description = modification_description
            lead.review_comment = f"MODIFIED by {actor.full_name}: {reason or 'Investigator notes added.'}"

        meta["review_history_log"] = history[-20:]

        lead.metadata_json = meta
        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)
        return lead
