"""Natural-Language Evidence Search and Retrieval-Augmented Generation (RAG) Service."""

from __future__ import annotations

import re
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.evidence import Evidence
from app.models.relationship import Relationship
from app.models.timeline import TimelineEvent


class RAGService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def search_evidence(self, case_id: UUID, query: str) -> dict[str, Any]:
        """
        Execute natural-language question answering / search strictly grounded
        in the case's digital evidence repository.
        Returns synthesized answer, citations, and supporting evidence references.
        """
        q = query.strip().lower()
        if not q:
            return {
                "query": query,
                "answer": "Please provide an investigation search query.",
                "citations": [],
                "matching_evidence": [],
            }

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
            .all()
        )

        # Tokenize query keywords
        tokens = [w for w in re.findall(r"\w+", q) if len(w) > 2 and w not in ("the", "and", "for", "with", "show", "what", "where", "who", "which")]

        matched_evidence = []
        citations = []

        for ev in evidence_items:
            combined_corpus = (
                f"{ev.original_name} {ev.description or ''} {ev.ocr_text or ''} "
                f"{ev.speech_transcript or ''} {str(ev.metadata_json or '')} "
                f"{str(ev.extracted_entities or '')}"
            ).lower()

            match_score = 0
            matching_snippets = []

            for token in tokens:
                if token in combined_corpus:
                    match_score += 1

            # Exact phrase matches
            if q in combined_corpus:
                match_score += 5

            if match_score > 0:
                # Extract relevant snippet
                snippet = ""
                for token in tokens:
                    idx = combined_corpus.find(token)
                    if idx != -1:
                        start = max(0, idx - 40)
                        end = min(len(combined_corpus), idx + 80)
                        snippet = "..." + combined_corpus[start:end].replace("\n", " ") + "..."
                        break

                ev_info = {
                    "id": str(ev.id),
                    "original_name": ev.original_name,
                    "file_type": ev.file_type,
                    "snippet": snippet or ev.description or "Evidence text match.",
                    "sha256": ev.sha256_hash,
                    "match_score": match_score,
                }
                matched_evidence.append(ev_info)
                citations.append({
                    "evidence_id": str(ev.id),
                    "evidence_name": ev.original_name,
                    "file_type": ev.file_type,
                    "reference": f"EV-{str(ev.id)[:8]}",
                })

        # Sort by relevance
        matched_evidence.sort(key=lambda x: x["match_score"], reverse=True)

        # Check relationships and timeline for matches
        related_entities = []
        for rel in relationships:
            if any(t in rel.target_label.lower() or t in rel.source_label.lower() for t in tokens):
                related_entities.append(f"{rel.source_label} ↔ {rel.target_label} ({rel.relationship_type.value})")

        # Synthesize explainable answer strictly grounded in evidence
        if not matched_evidence:
            answer = (
                f"No direct evidence match found in Case repository for '{query}'. "
                "Try searching by phone number, suspect name, location, or device identifier."
            )
        else:
            top_ev_names = [e["original_name"] for e in matched_evidence[:3]]
            answer_parts = [
                f"Found {len(matched_evidence)} relevant evidence source(s) referencing '{query}'.",
                f"Primary sources identified: {', '.join(top_ev_names)}.",
            ]
            if related_entities:
                answer_parts.append(f"Associated entity links: {'; '.join(related_entities[:3])}.")
            
            top_snippet = matched_evidence[0]["snippet"]
            if top_snippet:
                answer_parts.append(f"Key extract: \"{top_snippet}\"")
                
            answer_parts.append(
                "Recommendation: Inspect the cited evidence records below to review full original files."
            )
            answer = "\n\n".join(answer_parts)

        from app.services.ai.llm_service import DISCLAIMER, LLMService

        availability = LLMService.availability()
        grounded = "\n".join(
            f"{item['original_name']}: {item['snippet']}" for item in matched_evidence[:4]
        )
        answer = LLMService.interpret(
            task=f"Answer the investigator query using only cited evidence: {query}",
            grounded_text=grounded or "No matching evidence.",
            fallback=answer,
        )

        return {
            "query": query,
            "answer": answer,
            "citations": citations[:6],
            "sources": citations[:6],
            "matching_evidence": matched_evidence[:6],
            "total_matches": len(matched_evidence),
            "ai_mode": availability["mode"],
            "disclaimer": DISCLAIMER,
        }
