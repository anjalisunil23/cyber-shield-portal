"""AI Intelligence, Pipeline, Correlation, Risk Assessment, and Human Oversight Routes."""

from __future__ import annotations

import logging
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.enums import ActivityAction
from app.models.evidence import Evidence
from app.models.relationship import Relationship
from app.models.user import User
from app.services.activity import log_activity
from app.services.ai.correlation_service import CorrelationService
from app.services.ai.lead_service import LeadServiceAI
from app.services.ai.pipeline import EvidencePipeline
from app.services.ai.rag_service import RAGService
from app.services.ai.risk_service import RiskService
from app.services.ai.summary_service import SummaryService
from app.services.case_service import CaseService
from app.services.evidence_service import EvidenceService

logger = logging.getLogger("cybershield.ai")

router = APIRouter(tags=["ai-intelligence"])


class LeadReviewPayload(BaseModel):
    reason: str | None = None
    title: str | None = None
    description: str | None = None


class AISearchRequest(BaseModel):
    query: str = Field(..., min_length=1)


# ---- 1. Single Evidence Processing & Analysis ----

@router.post("/evidence/{evidence_id}/process")
def process_single_evidence(
    evidence_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """Execute or re-run automated extraction & AI preprocessing on a single evidence file."""
    ev = EvidenceService(db).get(evidence_id)
    CaseService(db).verify_case_access(user, ev.case_id)

    log_activity(
        db,
        user_id=user.id,
        case_id=ev.case_id,
        action=ActivityAction.update,
        resource_type="evidence",
        resource_id=str(evidence_id),
        description=f"Triggered AI processing pipeline for {ev.original_name}",
    )
    db.commit()

    pipeline = EvidencePipeline(db)
    result = pipeline.process_single_evidence(evidence_id)
    return result


@router.get("/evidence/{evidence_id}/analysis")
def get_evidence_analysis(
    evidence_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """Retrieve deep forensic intelligence, metadata, OCR, transcript, and normalized entities for an evidence file."""
    ev = EvidenceService(db).get(evidence_id)
    CaseService(db).verify_case_access(user, ev.case_id)

    entities = []
    if isinstance(ev.extracted_entities, list):
        entities = ev.extracted_entities
    elif isinstance(ev.extracted_entities, dict) and "entities" in ev.extracted_entities:
        entities = ev.extracted_entities["entities"]

    ai_meta = ev.ai_metadata or {}
    steps = ai_meta.get("pipeline_steps") or {}

    return {
        "id": str(ev.id),
        "case_id": str(ev.case_id),
        "original_name": ev.original_name,
        "filename": ev.filename,
        "file_type": ev.file_type,
        "mime_type": ev.mime_type,
        "file_size": ev.file_size,
        "sha256_hash": ev.sha256_hash,
        "upload_date": ev.upload_date.isoformat() if ev.upload_date else None,
        "is_duplicate": ev.is_duplicate,
        "duplicate_of_id": str(ev.duplicate_of_id) if ev.duplicate_of_id else None,
        "duplicate_warning": (ev.metadata_json or {}).get("duplicate_warning") if ev.is_duplicate else None,
        "processing_status": ai_meta.get("processing_status", "PROCESSED" if (ev.ocr_text or ev.extracted_entities) else "UPLOADED"),
        "pipeline_steps": steps,
        "metadata": ev.metadata_json or {},
        "ocr_text": ev.ocr_text or "",
        "ocr_engine": steps.get("ocr_engine", "none"),
        "ocr_confidence": steps.get("ocr_confidence", 0.0),
        "speech_transcript": ev.speech_transcript or "",
        "stt_engine": steps.get("stt_engine", "none"),
        "extracted_entities": entities,
        "entity_count": len(entities),
        "risk_score": ev.risk_score,
        "disclaimer": (
            "Cyber Shield AI analysis is decision-support only. "
            "All findings, entities, and transcripts must be verified by the assigned investigator."
        ),
    }


# ---- 2. Case-Level Intelligence Pipeline ----

@router.post("/cases/{case_id}/pipeline")
def run_case_pipeline(
    case_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """Execute end-to-end evidence pipeline: Ingestion -> Content Extraction -> Entities -> Correlation -> Timeline -> Risk -> Explainable Leads."""
    CaseService(db).verify_case_access(user, case_id)

    pipeline = EvidencePipeline(db)
    result = pipeline.run_case_pipeline(case_id=case_id, actor_id=user.id)

    log_activity(
        db,
        user_id=user.id,
        case_id=case_id,
        action=ActivityAction.create,
        resource_type="case",
        resource_id=str(case_id),
        description=f"Executed AI intelligence pipeline (Generated {result.get('leads_generated', 0)} leads, Risk: {result.get('risk_score', 0)})",
    )
    db.commit()

    return result


@router.get("/cases/{case_id}/correlations")
def get_case_correlations(
    case_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> list[dict[str, Any]]:
    """Retrieve cross-source entity correlations identifying shared phone numbers, emails, devices, or persons across evidence files."""
    CaseService(db).verify_case_access(user, case_id)
    correlator = CorrelationService(db)
    return correlator.correlate_case_evidence(case_id)


@router.get("/cases/{case_id}/entities")
def get_case_entities(
    case_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> list[dict[str, Any]]:
    """Retrieve all aggregated normalized entities extracted from digital evidence in this case."""
    CaseService(db).verify_case_access(user, case_id)
    evidence_items = db.query(Evidence).filter(Evidence.case_id == case_id).all()

    entity_map: dict[str, dict[str, Any]] = {}
    for ev in evidence_items:
        items = []
        if isinstance(ev.extracted_entities, list):
            items = ev.extracted_entities
        elif isinstance(ev.extracted_entities, dict) and "entities" in ev.extracted_entities:
            items = ev.extracted_entities["entities"]

        for ent in items:
            key = f"{ent.get('type')}:{ent.get('normalized_value', ent.get('raw_value'))}"
            if key not in entity_map:
                entity_map[key] = {
                    "type": ent.get("type"),
                    "raw_value": ent.get("raw_value"),
                    "normalized_value": ent.get("normalized_value"),
                    "confidence": ent.get("confidence", 0.9),
                    "occurrences": 1,
                    "evidence_ids": [str(ev.id)],
                    "evidence_names": [ev.original_name],
                    "contexts": [ent.get("context")] if ent.get("context") else [],
                }
            else:
                entity_map[key]["occurrences"] += 1
                if str(ev.id) not in entity_map[key]["evidence_ids"]:
                    entity_map[key]["evidence_ids"].append(str(ev.id))
                    entity_map[key]["evidence_names"].append(ev.original_name)
                if ent.get("context") and ent.get("context") not in entity_map[key]["contexts"]:
                    entity_map[key]["contexts"].append(ent.get("context"))

    return sorted(list(entity_map.values()), key=lambda x: (x["occurrences"], len(x["evidence_ids"])), reverse=True)


@router.get("/cases/{case_id}/risk")
def get_case_risk(
    case_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """Retrieve transparent, factor-based risk score (0-100) and priority level with explanation."""
    CaseService(db).verify_case_access(user, case_id)
    risk_svc = RiskService(db)
    return risk_svc.assess_case_risk(case_id)


@router.get("/cases/{case_id}/graph")
def get_case_graph(
    case_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """Retrieve nodes and edges for dynamic interactive relationship graph visualization."""
    CaseService(db).verify_case_access(user, case_id)

    relationships = (
        db.query(Relationship)
        .filter(Relationship.case_id == case_id)
        .all()
    )

    evidence_items = (
        db.query(Evidence)
        .filter(Evidence.case_id == case_id)
        .all()
    )

    nodes_dict: dict[str, dict[str, Any]] = {}
    edges = []

    # 1. Add evidence nodes
    for ev in evidence_items:
        node_id = f"ev_{ev.id}"
        nodes_dict[node_id] = {
            "id": node_id,
            "label": ev.original_name,
            "kind": "evidence",
            "evidence_id": str(ev.id),
            "file_type": ev.file_type,
            "color": "#38BDF8",  # cyan/blue
            "size": 22,
        }

    # 2. Add relationship edges and target entity nodes
    for rel in relationships:
        src_id = f"ev_{rel.source_id}" if rel.source_kind.value == "evidence" else f"node_{rel.source_id}"
        if src_id not in nodes_dict:
            nodes_dict[src_id] = {
                "id": src_id,
                "label": rel.source_label,
                "kind": rel.source_kind.value,
                "color": "#94A3B8",
                "size": 18,
            }

        tgt_id = f"node_{rel.target_id}"
        if tgt_id not in nodes_dict:
            # Color code based on target kind
            kind_str = rel.target_kind.value
            color_map = {
                "person": "#34D399",     # emerald
                "phone": "#22D3EE",      # cyan
                "email": "#A78BFA",      # violet
                "device": "#38BDF8",     # sky
                "location": "#F472B6",   # pink
                "organization": "#FBBF24", # amber
            }
            nodes_dict[tgt_id] = {
                "id": tgt_id,
                "label": rel.target_label,
                "kind": kind_str,
                "color": color_map.get(kind_str, "#94A3B8"),
                "size": 20,
            }

        edges.append({
            "id": str(rel.id),
            "source": src_id,
            "target": tgt_id,
            "type": rel.relationship_type.value,
            "label": rel.relationship_type.value.replace("_", " "),
            "confidence": rel.confidence or 0.85,
            "ai_generated": rel.ai_generated,
            "description": rel.description or "",
        })

    return {
        "case_id": str(case_id),
        "nodes": list(nodes_dict.values()),
        "edges": edges,
    }


@router.post("/cases/{case_id}/search")
def search_case_evidence(
    case_id: UUID,
    payload: AISearchRequest,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """Execute grounded natural-language search across the case's evidence repository (RAG)."""
    CaseService(db).verify_case_access(user, case_id)
    rag = RAGService(db)
    return rag.search_evidence(case_id, payload.query)


@router.post("/cases/{case_id}/summarize")
def summarize_case(
    case_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """Generate structured AI-assisted investigation summary with clear human-verification demarcation."""
    CaseService(db).verify_case_access(user, case_id)
    summary_svc = SummaryService(db)
    summary = summary_svc.generate_case_summary(case_id)

    log_activity(
        db,
        user_id=user.id,
        case_id=case_id,
        action=ActivityAction.create,
        resource_type="report",
        description="Generated structured AI investigation intelligence summary",
    )
    db.commit()

    return summary


# ---- 3. Human Oversight Review Workflow ----

def _lead_with_access(db: Session, user: User, lead_id: UUID):
    from app.models.lead import ManualLead

    lead = db.get(ManualLead, lead_id)
    if not lead:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Lead not found")
    CaseService(db).verify_case_access(user, lead.case_id)
    return lead


@router.get("/ai/status")
def ai_engine_status(
    _: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """Report configured vs fallback intelligence engines without exposing secrets."""
    from app.services.ai.llm_service import LLMService
    from app.services.ai.ocr_service import OCRService
    from app.services.ai.transcription_service import TranscriptionService

    llm = LLMService.availability()
    return {
        "llm": llm,
        "ocr_engine": OCRService.get_available_engine(),
        "stt_engine": TranscriptionService.get_available_engine(),
        "mode": "configured" if llm["available"] else "fallback",
        "disclaimer": llm["disclaimer"],
    }


@router.get("/cases/{case_id}/audit-log")
def case_audit_log(
    case_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
) -> dict[str, Any]:
    from app.repositories.common import ActivityRepository
    from app.schemas.domain import ActivityOut
    from app.utils.pagination import paginate

    CaseService(db).verify_case_access(user, case_id)
    items, total = ActivityRepository(db).list(
        offset=(page - 1) * page_size, limit=page_size, case_id=case_id
    )
    return paginate(total, page, page_size, [ActivityOut.model_validate(i) for i in items]).model_dump()


@router.get("/cases/{case_id}/intelligence-export")
def export_case_intelligence(
    case_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """JSON export of case intelligence, clearly labeling AI vs investigator-verified content."""
    CaseService(db).verify_case_access(user, case_id)
    from app.services.ai.summary_service import SummaryService
    from app.services.ai.risk_service import RiskService
    from app.services.ai.correlation_service import CorrelationService

    summary = SummaryService(db).generate_case_summary(case_id)
    risk = RiskService(db).assess_case_risk(case_id)
    correlations = CorrelationService(db).correlate_case_evidence(case_id)
    return {
        "export_type": "case_intelligence",
        "generated_for": user.full_name,
        "summary": summary,
        "risk": risk,
        "correlations": correlations,
        "disclaimer": (
            "Cyber Shield is an investigation support and decision-assistance platform. "
            "AI-generated findings are recommendations only and must be independently verified "
            "by authorized investigators."
        ),
    }


@router.post("/leads/{lead_id}/verify")
def verify_lead(
    lead_id: UUID,
    payload: LeadReviewPayload,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """Human investigator verifies an AI-generated lead after independent evidentiary review."""
    _lead_with_access(db, user, lead_id)
    lead_svc = LeadServiceAI(db)
    lead = lead_svc.review_lead(
        lead_id=lead_id,
        action="verify",
        actor=user,
        reason=payload.reason,
    )

    log_activity(
        db,
        user_id=user.id,
        case_id=lead.case_id,
        action=ActivityAction.approve,
        resource_type="lead",
        resource_id=str(lead_id),
        description=f"Investigator {user.full_name} verified AI lead: {lead.title}",
    )
    db.commit()

    return {
        "success": True,
        "lead_id": str(lead.id),
        "status": lead.status.value,
        "review_state": "VERIFIED",
        "comment": lead.review_comment,
    }


@router.post("/leads/{lead_id}/reject")
def reject_lead(
    lead_id: UUID,
    payload: LeadReviewPayload,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """Human investigator rejects an AI-generated lead deemed non-viable or irrelevant."""
    _lead_with_access(db, user, lead_id)
    lead_svc = LeadServiceAI(db)
    lead = lead_svc.review_lead(
        lead_id=lead_id,
        action="reject",
        actor=user,
        reason=payload.reason,
    )

    log_activity(
        db,
        user_id=user.id,
        case_id=lead.case_id,
        action=ActivityAction.request_changes,
        resource_type="lead",
        resource_id=str(lead_id),
        description=f"Investigator {user.full_name} rejected AI lead: {lead.title}",
    )
    db.commit()

    return {
        "success": True,
        "lead_id": str(lead.id),
        "status": lead.status.value,
        "review_state": "REJECTED",
        "comment": lead.review_comment,
    }


@router.post("/leads/{lead_id}/modify")
def modify_lead(
    lead_id: UUID,
    payload: LeadReviewPayload,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """Human investigator modifies an AI-generated lead with domain notes while preserving original AI context."""
    _lead_with_access(db, user, lead_id)
    lead_svc = LeadServiceAI(db)
    lead = lead_svc.review_lead(
        lead_id=lead_id,
        action="modify",
        actor=user,
        modification_title=payload.title,
        modification_description=payload.description,
        reason=payload.reason,
    )

    log_activity(
        db,
        user_id=user.id,
        case_id=lead.case_id,
        action=ActivityAction.update,
        resource_type="lead",
        resource_id=str(lead_id),
        description=f"Investigator {user.full_name} modified AI lead: {lead.title}",
    )
    db.commit()

    return {
        "success": True,
        "lead_id": str(lead.id),
        "title": lead.title,
        "status": lead.status.value,
        "review_state": "MODIFIED",
        "comment": lead.review_comment,
    }


# ---- 4. Demonstration Synthetic Seeder Endpoint ----

@router.post("/demo/seed-synthetic-case")
def seed_synthetic_demo(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """Create or reset synthetic demonstration case CS-2026-0003 with realistic multi-source evidence and pipeline analysis."""
    from seed_synthetic_case import seed_case_cs2026_0003
    result = seed_case_cs2026_0003(db, user)
    return result
