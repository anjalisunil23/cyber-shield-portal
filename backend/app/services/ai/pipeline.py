"""Master Evidence Intelligence Pipeline Runner for Cyber Shield."""

from __future__ import annotations

import datetime
import logging
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.enums import NotificationType
from app.models.evidence import Evidence
from app.models.case import Case
from app.services.ai.correlation_service import CorrelationService
from app.services.ai.entity_service import EntityService
from app.services.ai.hash_service import HashService
from app.services.ai.lead_service import LeadServiceAI
from app.services.ai.metadata_service import MetadataService
from app.services.ai.ocr_service import OCRService
from app.services.ai.risk_service import RiskService
from app.services.ai.text_service import TextService
from app.services.ai.timeline_service import TimelineService
from app.services.ai.transcription_service import TranscriptionService
from app.services.notifications import notify
from app.services.storage import get_storage

logger = logging.getLogger("cybershield.ai.pipeline")


class EvidencePipeline:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.storage = get_storage()

    def process_single_evidence(self, evidence_id: UUID) -> dict[str, Any]:
        """
        Execute full extraction & AI preprocessing for a single evidence item.
        Updates evidence.ocr_text, speech_transcript, extracted_entities, metadata_json,
        and ai_metadata with pipeline status.
        Never raises fatal exceptions that crash caller.
        """
        ev = self.db.get(Evidence, evidence_id)
        if not ev:
            return {"success": False, "message": "Evidence not found"}

        # Read original bytes safely
        try:
            file_path = self.storage.open_path(ev.storage_path)
            with open(file_path, "rb") as f:
                data = f.read()
        except Exception as e:
            ev.ai_metadata = {
                "processing_status": "FAILED",
                "error": f"Failed to read evidence file: {str(e)}",
            }
            self.db.commit()
            return {"success": False, "message": f"Storage read error: {str(e)}"}

        logger.info("Evidence processing started: %s (%s)", ev.id, ev.original_name)

        ev.ai_metadata = {
            "processing_status": "PROCESSING",
            "pipeline_steps": {
                "hash_verification": "PROCESSING",
                "metadata_extraction": "PENDING",
                "content_extraction": "PENDING",
                "entity_extraction": "PENDING",
            },
        }
        self.db.add(ev)
        self.db.commit()

        # Track pipeline step completion
        pipeline_steps = {
            "hash_verification": "PENDING",
            "metadata_extraction": "PENDING",
            "content_extraction": "PENDING",
            "entity_extraction": "PENDING",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }

        # 0. Hash integrity verification (never rewrite original file)
        try:
            computed = HashService.calculate_sha256(data)
            if ev.sha256_hash and computed != ev.sha256_hash:
                pipeline_steps["hash_verification"] = "FAILED"
                pipeline_steps["hash_mismatch"] = True
                logger.warning("Hash mismatch for evidence %s", ev.id)
            else:
                pipeline_steps["hash_verification"] = "COMPLETED"
                pipeline_steps["sha256"] = computed
                if not ev.sha256_hash:
                    ev.sha256_hash = computed
        except Exception as e:
            pipeline_steps["hash_verification"] = f"PARTIAL: {str(e)}"

        # 1. Metadata Extraction
        try:
            meta = MetadataService.extract_all_metadata(data, ev.original_name, ev.file_type, ev.mime_type)
            # Preserve existing duplicate warning if present
            if ev.metadata_json and "duplicate_warning" in ev.metadata_json:
                meta["duplicate_warning"] = ev.metadata_json["duplicate_warning"]
            ev.metadata_json = meta
            pipeline_steps["metadata_extraction"] = "COMPLETED"
        except Exception as e:
            pipeline_steps["metadata_extraction"] = f"PARTIAL: {str(e)}"

        # 2. Text / OCR / Audio Content Extraction
        pipeline_steps["content_extraction"] = "PROCESSING"
        extracted_text = ""

        try:
            if ev.file_type == "image":
                ocr_result = OCRService.run_ocr(data)
                ev.ocr_text = ocr_result.get("text", "")
                extracted_text = ev.ocr_text
                pipeline_steps["ocr_engine"] = ocr_result.get("engine", "none")
                pipeline_steps["ocr_confidence"] = ocr_result.get("confidence", 0.0)

            elif ev.file_type in ("audio", "video"):
                stt_result = TranscriptionService.transcribe(data, ev.original_name)
                ev.speech_transcript = stt_result.get("transcript", "")
                extracted_text = ev.speech_transcript
                pipeline_steps["stt_engine"] = stt_result.get("engine", "none")

            else:
                # Documents, emails, chat logs, csv, json, txt
                extracted_text = TextService.extract_text_from_bytes(
                    data, ev.original_name, ev.file_type, ev.mime_type
                )
                ev.ocr_text = extracted_text  # store document text in ocr_text for universal access

            pipeline_steps["content_extraction"] = "COMPLETED"
        except Exception as e:
            pipeline_steps["content_extraction"] = f"PARTIAL: {str(e)}"

        # 3. Entity Extraction & Normalization
        pipeline_steps["entity_extraction"] = "PROCESSING"
        try:
            entities = EntityService.extract_entities_from_text(
                extracted_text, evidence_id=str(ev.id)
            )
            ev.extracted_entities = {
                "count": len(entities),
                "entities": entities,
            }
            pipeline_steps["entity_extraction"] = "COMPLETED"
            pipeline_steps["entities_found"] = len(entities)
        except Exception as e:
            pipeline_steps["entity_extraction"] = f"FAILED: {str(e)}"

        # 4. Finalize Status
        is_partial = any("PARTIAL" in str(v) for v in pipeline_steps.values())
        status_val = "PARTIALLY_PROCESSED" if is_partial else "PROCESSED"

        ev.ai_metadata = {
            "processing_status": status_val,
            "pipeline_steps": pipeline_steps,
            "processed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }

        self.db.add(ev)
        self.db.commit()
        self.db.refresh(ev)
        logger.info("Evidence processing completed: %s status=%s", ev.id, status_val)

        return {
            "success": True,
            "evidence_id": str(ev.id),
            "status": status_val,
            "pipeline_steps": pipeline_steps,
        }

    def run_case_pipeline(self, case_id: UUID, actor_id: UUID) -> dict[str, Any]:
        """
        Execute the end-to-end intelligence pipeline across all evidence items in a case:
        Evidence Ingestion -> OCR / Text / STT -> Entities -> Correlation -> Timeline -> Risk -> Explainable Leads.
        """
        evidence_items = (
            self.db.query(Evidence)
            .filter(Evidence.case_id == case_id)
            .all()
        )

        processed_count = 0
        for ev in evidence_items:
            res = self.process_single_evidence(ev.id)
            if res.get("success"):
                processed_count += 1

        # 1. Cross-Source Correlation
        correlator = CorrelationService(self.db)
        correlations = correlator.correlate_case_evidence(case_id)

        # 2. Timeline Reconstruction
        timeline_svc = TimelineService(self.db)
        timeline_events = timeline_svc.reconstruct_timeline(case_id)

        # 3. Risk Assessment
        risk_svc = RiskService(self.db)
        risk_result = risk_svc.assess_case_risk(case_id)

        # 4. Explainable Lead Generation
        lead_svc = LeadServiceAI(self.db)
        generated_leads = lead_svc.generate_explainable_leads(
            case_id=case_id,
            correlations=correlations,
            risk_assessment=risk_result,
            actor_id=actor_id,
        )

        case = self.db.get(Case, case_id)
        if case:
            for a in case.assignments:
                notify(
                    self.db,
                    user_id=a.user_id,
                    notification_type=NotificationType.lead_created if generated_leads else NotificationType.general,
                    title="AI analysis completed",
                    message=(
                        f"Pipeline finished for {case.case_number}: "
                        f"{len(generated_leads)} lead(s), risk {risk_result.get('risk_level', 'n/a')}."
                    ),
                    link=f"/dashboard/cases/{case_id}",
                )
            self.db.commit()

        logger.info(
            "Case pipeline completed: %s evidence=%s correlations=%s leads=%s risk=%s",
            case_id,
            processed_count,
            len(correlations),
            len(generated_leads),
            risk_result.get("risk_score"),
        )

        return {
            "success": True,
            "case_id": str(case_id),
            "evidence_processed": processed_count,
            "total_evidence": len(evidence_items),
            "correlations_found": len(correlations),
            "correlations": correlations,
            "timeline_events_generated": len(timeline_events),
            "risk_score": risk_result["risk_score"],
            "risk_level": risk_result["risk_level"],
            "leads_generated": len(generated_leads),
        }
