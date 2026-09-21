"""Automated Timeline Reconstruction Engine from Multi-Source Digital Evidence."""

from __future__ import annotations

import datetime
import re
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.enums import TimelineEventType
from app.models.evidence import Evidence
from app.models.timeline import TimelineEvent


class TimelineService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def reconstruct_timeline(self, case_id: UUID) -> list[dict[str, Any]]:
        """
        Extract chronological milestones from EXIF timestamps, chat messages, call logs,
        document headers, and transcripts, creating evidence-linked timeline entries.
        """
        evidence_items = (
            self.db.query(Evidence)
            .filter(Evidence.case_id == case_id)
            .all()
        )

        extracted_events: list[dict[str, Any]] = []

        for ev in evidence_items:
            # 1. Image EXIF timestamp (Exact timestamp)
            meta = ev.metadata_json or {}
            exif = meta.get("exif") or {}
            dt_orig = exif.get("DateTimeOriginal")
            if dt_orig:
                # Format: YYYY:MM:DD HH:MM:SS -> ISO
                try:
                    dt_clean = dt_orig.replace(":", "-", 2)
                    parsed_dt = datetime.datetime.fromisoformat(dt_clean)
                    extracted_events.append({
                        "event_at": parsed_dt,
                        "title": f"CCTV Frame Captured: {ev.original_name}",
                        "description": f"Camera timestamp recorded at {dt_orig}. " + (
                            f"Location: {meta.get('gps_coordinates')}" if meta.get("gps_coordinates") != "Not Available" else ""
                        ),
                        "evidence_id": ev.id,
                        "evidence_name": ev.original_name,
                        "timestamp_nature": "Exact timestamp",
                        "confidence": 0.95,
                    })
                except Exception:
                    pass

            # 2. Text / Chat / Call Log Timestamps
            text_content = ""
            if ev.ocr_text:
                text_content += f"\n{ev.ocr_text}"
            if ev.speech_transcript:
                text_content += f"\n{ev.speech_transcript}"

            # Parse lines from chat / call records (e.g. "[2026-08-01 20:30:15] +919876543210: ...")
            timestamped_lines = re.finditer(
                r"(?:\[|\b)(\d{4}[-/]\d{1,2}[-/]\d{1,2}[ T]\d{1,2}:\d{2}(?::\d{2})?)(?:\]|\b)(?:[ -:]+)(.+)",
                text_content,
            )

            for match in timestamped_lines:
                dt_str = match.group(1).replace("/", "-")
                line_desc = match.group(2).strip()[:180]
                try:
                    parsed_dt = datetime.datetime.fromisoformat(dt_str)
                    extracted_events.append({
                        "event_at": parsed_dt,
                        "title": f"Logged Communication: {ev.original_name}",
                        "description": line_desc,
                        "evidence_id": ev.id,
                        "evidence_name": ev.original_name,
                        "timestamp_nature": "Exact timestamp",
                        "confidence": 0.92,
                    })
                except Exception:
                    pass

        # Sort chronologically
        extracted_events.sort(key=lambda x: x["event_at"])

        # Create or sync TimelineEvent records
        for item in extracted_events:
            # Check if this exact event is already logged
            existing = (
                self.db.query(TimelineEvent)
                .filter(
                    TimelineEvent.case_id == case_id,
                    TimelineEvent.related_evidence_id == item["evidence_id"],
                    TimelineEvent.title == item["title"],
                )
                .first()
            )

            if not existing:
                new_event = TimelineEvent(
                    case_id=case_id,
                    event_type=TimelineEventType.manual,
                    title=item["title"],
                    description=item["description"],
                    event_at=item["event_at"],
                    related_evidence_id=item["evidence_id"],
                    metadata_json={
                        "timestamp_nature": item["timestamp_nature"],
                        "confidence": item["confidence"],
                        "evidence_name": item["evidence_name"],
                    },
                )
                self.db.add(new_event)

        self.db.commit()
        return extracted_events
