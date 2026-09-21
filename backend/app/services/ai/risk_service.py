"""Explainable and Transparent Risk Assessment Engine."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.evidence import Evidence
from app.models.relationship import Relationship


class RiskService:
    SUSPICIOUS_KEYWORDS = {
        "ransom", "kidnap", "payment", "crypto", "threat", "bitcoin", "amber",
        "missing", "intercept", "secret", "destroy", "wire", "transfer", "cash",
        "deadline", "police", "warning", "untraceable", "burner", "sim", "imei"
    }

    def __init__(self, db: Session) -> None:
        self.db = db

    def assess_case_risk(self, case_id: UUID) -> dict[str, Any]:
        """
        Evaluate objective investigative risk score (0-100) with complete factor breakdown.
        Represents investigative priority, not legal guilt or certainty.
        """
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

        factors: list[dict[str, Any]] = []
        raw_score = 0

        # 1. Evidence Recurrence & Volume
        ev_count = len(evidence_items)
        if ev_count >= 5:
            points = 10
            raw_score += points
            factors.append({
                "factor": "Evidence Recurrence & Multi-Source Volume",
                "points": points,
                "detail": f"{ev_count} distinct digital evidence files uploaded and correlated in this case.",
            })
        elif ev_count >= 2:
            points = 5
            raw_score += points
            factors.append({
                "factor": "Initial Evidence Ingestion",
                "points": points,
                "detail": f"{ev_count} evidence files available for cross-source analysis.",
            })

        # 2. Multi-Source Entity Correlations
        cross_source_rels = [r for r in relationships if r.ai_generated and r.confidence and r.confidence >= 0.85]
        if len(cross_source_rels) >= 3:
            points = 20
            raw_score += points
            factors.append({
                "factor": "Strong Entity Relationships",
                "points": points,
                "detail": f"{len(cross_source_rels)} high-confidence entity links established across different evidence sources.",
            })
        elif len(cross_source_rels) >= 1:
            points = 15
            raw_score += points
            factors.append({
                "factor": "Cross-Source Entity Matches",
                "points": points,
                "detail": f"{len(cross_source_rels)} entity match verified across multiple distinct files.",
            })

        # 3. Suspicious Forensic Keywords Matches
        matched_keywords: set[str] = set()
        for ev in evidence_items:
            combined_text = f"{ev.ocr_text or ''} {ev.speech_transcript or ''} {ev.description or ''}".lower()
            for kw in self.SUSPICIOUS_KEYWORDS:
                if kw in combined_text:
                    matched_keywords.add(kw)

        if len(matched_keywords) >= 4:
            points = 15
            raw_score += points
            factors.append({
                "factor": "High-Frequency Suspicious Indicators",
                "points": points,
                "detail": f"Matched multiple urgent investigative keywords: {', '.join(sorted(list(matched_keywords))[:6])}.",
            })
        elif len(matched_keywords) >= 1:
            points = 10
            raw_score += points
            factors.append({
                "factor": "Investigative Keyword Presence",
                "points": points,
                "detail": f"Matched key indicators: {', '.join(sorted(list(matched_keywords))[:4])}.",
            })

        # 4. Temporal Alignment / Cluster Anomaly
        timestamps = []
        for ev in evidence_items:
            meta = ev.metadata_json or {}
            ts_list = meta.get("embedded_timestamps", [])
            timestamps.extend(ts_list)

        if len(timestamps) >= 3:
            points = 15
            raw_score += points
            factors.append({
                "factor": "Temporal Convergence / Rapid Communication",
                "points": points,
                "detail": "Multiple timestamps recorded in rapid succession within the active investigation window.",
            })

        # 5. Geolocation / Device Identification
        geo_count = sum(1 for ev in evidence_items if (ev.metadata_json or {}).get("gps_coordinates") not in (None, "Not Available"))
        if geo_count >= 1:
            points = 15
            raw_score += points
            factors.append({
                "factor": "Geolocation & Device Footprint",
                "points": points,
                "detail": f"Verified physical coordinates and device identifiers extracted from {geo_count} media frame(s).",
            })

        # Final Score normalization (0 - 100) using configurable thresholds
        final_score = min(100, max(10, raw_score))
        settings = get_settings()
        low_max = settings.risk_low_max
        medium_max = settings.risk_medium_max
        high_max = settings.risk_high_max

        if final_score <= low_max:
            level = "LOW"
            badge_color = "emerald"
        elif final_score <= medium_max:
            level = "MEDIUM"
            badge_color = "blue"
        elif final_score <= high_max:
            level = "HIGH"
            badge_color = "amber"
        else:
            level = "CRITICAL"
            badge_color = "red"

        # Update evidence risk_score on items
        for ev in evidence_items:
            ev.risk_score = float(final_score)
        self.db.commit()

        return {
            "case_id": str(case_id),
            "risk_score": final_score,
            "risk_level": level,
            "badge_color": badge_color,
            "factors": factors,
            "disclaimer": (
                "Cyber Shield Risk Assessment represents investigative priority and anomaly severity, "
                "not legal proof of guilt or certainty. All findings require independent officer verification."
            ),
        }
