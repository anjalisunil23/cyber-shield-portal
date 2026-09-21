"""Cross-Source Entity Correlation and Evidence Relationship Generation Engine."""

from __future__ import annotations

from collections import defaultdict
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.enums import EntityKind, RelationshipType
from app.models.evidence import Evidence
from app.models.relationship import Relationship


class CorrelationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def correlate_case_evidence(self, case_id: UUID) -> list[dict[str, Any]]:
        """
        Scan all evidence records for a case, cluster matching normalized entities,
        and generate explainable cross-source relationships with confidence and evidence citations.
        """
        evidence_items = (
            self.db.query(Evidence)
            .filter(Evidence.case_id == case_id)
            .all()
        )

        if not evidence_items:
            return []

        # Map: (entity_type, normalized_value) -> list of {evidence_id, original_name, raw_value, context}
        entity_clusters: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)

        for ev in evidence_items:
            entities = []
            if isinstance(ev.extracted_entities, list):
                entities = ev.extracted_entities
            elif isinstance(ev.extracted_entities, dict) and "entities" in ev.extracted_entities:
                entities = ev.extracted_entities["entities"]

            for ent in entities:
                ent_type = ent.get("type", "UNKNOWN")
                norm_val = ent.get("normalized_value", "").strip()
                if not norm_val or len(norm_val) < 3:
                    continue

                entity_clusters[(ent_type, norm_val)].append({
                    "evidence_id": str(ev.id),
                    "evidence_name": ev.original_name,
                    "evidence_type": ev.file_type,
                    "raw_value": ent.get("raw_value", norm_val),
                    "context": ent.get("context", ""),
                })

        correlations: list[dict[str, Any]] = []

        # Find entities appearing in 2 or more distinct evidence files
        for (ent_type, norm_val), occurrences in entity_clusters.items():
            distinct_ev_ids = list({occ["evidence_id"] for occ in occurrences})
            if len(distinct_ev_ids) < 2:
                continue

            supporting_evidence_names = list({occ["evidence_name"] for occ in occurrences})
            supporting_types = list({occ["evidence_type"] for occ in occurrences})

            # Calculate correlation confidence: base 0.85 + bonus for multi-modal sources
            confidence = min(0.98, round(0.85 + (len(supporting_types) * 0.04), 2))

            explanation = (
                f"The normalized entity '{norm_val}' ({ent_type}) recurred across "
                f"{len(distinct_ev_ids)} distinct evidence files: {', '.join(supporting_evidence_names)}."
            )

            correlations.append({
                "entity_type": ent_type,
                "normalized_value": norm_val,
                "evidence_count": len(distinct_ev_ids),
                "supporting_evidence_ids": distinct_ev_ids,
                "supporting_evidence_names": supporting_evidence_names,
                "confidence_score": confidence,
                "explanation": explanation,
            })

            # Map to domain RelationshipType & EntityKind
            target_kind = EntityKind.other
            rel_type = RelationshipType.other

            if ent_type == "PERSON":
                target_kind = EntityKind.person
                rel_type = RelationshipType.evidence_to_person
            elif ent_type == "PHONE":
                target_kind = EntityKind.phone
                rel_type = RelationshipType.evidence_to_device
            elif ent_type == "EMAIL":
                target_kind = EntityKind.email
                rel_type = RelationshipType.evidence_to_person
            elif ent_type == "LOCATION":
                target_kind = EntityKind.location
                rel_type = RelationshipType.evidence_to_location
            elif ent_type == "DEVICE":
                target_kind = EntityKind.device
                rel_type = RelationshipType.evidence_to_device

            # Create or update Relationship edge from primary evidence to entity
            for ev_id in distinct_ev_ids:
                existing_rel = (
                    self.db.query(Relationship)
                    .filter(
                        Relationship.case_id == case_id,
                        Relationship.source_id == ev_id,
                        Relationship.target_label == norm_val,
                    )
                    .first()
                )

                ev_name = next(
                    (occ["evidence_name"] for occ in occurrences if occ["evidence_id"] == ev_id),
                    "Evidence",
                )

                if not existing_rel:
                    new_rel = Relationship(
                        case_id=case_id,
                        relationship_type=rel_type,
                        source_kind=EntityKind.evidence,
                        source_id=ev_id,
                        source_label=ev_name,
                        target_kind=target_kind,
                        target_id=norm_val,
                        target_label=norm_val,
                        description=explanation,
                        ai_generated=True,
                        confidence=confidence,
                        metadata_json={
                            "correlation_type": ent_type,
                            "supporting_evidence_ids": distinct_ev_ids,
                            "explanation": explanation,
                        },
                    )
                    self.db.add(new_rel)
                else:
                    existing_rel.confidence = confidence
                    existing_rel.description = explanation
                    existing_rel.metadata_json = {
                        "correlation_type": ent_type,
                        "supporting_evidence_ids": distinct_ev_ids,
                        "explanation": explanation,
                    }

        self.db.commit()
        return correlations
