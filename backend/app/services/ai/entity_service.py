"""Forensic Entity Extraction, Normalization, and Context Preservation Engine."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse


class EntityService:
    # Compile regex patterns for high-precision entity detection
    EMAIL_REGEX = re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", re.IGNORECASE
    )
    
    # Matches international and domestic phone formats (+91 98765 43210, 9876543210, (555) 123-4567, etc.)
    PHONE_REGEX = re.compile(
        r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,5}[-.\s]?\d{3,5}\b"
    )

    URL_REGEX = re.compile(
        r"\bhttps?://[^\s<>\"{}|\\^`]+|\bwww\.[^\s<>\"{}|\\^`]+\.[a-z]{2,}\b", re.IGNORECASE
    )

    # IP Address
    IP_REGEX = re.compile(
        r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b"
    )

    # MAC Address
    MAC_REGEX = re.compile(
        r"\b(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})\b"
    )

    # IMEI (15 digits)
    IMEI_REGEX = re.compile(r"\b\d{15}\b")

    # Dates (YYYY-MM-DD, DD/MM/YYYY, Month DD, YYYY)
    DATE_REGEX = re.compile(
        r"\b(?:\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|"
        r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})\b",
        re.IGNORECASE,
    )

    # Times (HH:MM:SS, HH:MM AM/PM)
    TIME_REGEX = re.compile(
        r"\b(?:[01]?\d|2[0-3]):[0-5]\d(?::[0-5]\d)?(?:\s*(?:AM|PM|am|pm))?\b"
    )

    # Vehicle Plate Patterns (e.g., KL-07-CD-4921, MH 12 AB 1234, DL-3C-1234)
    PLATE_REGEX = re.compile(
        r"\b[A-Z]{2}[-\s]?\d{1,2}[-\s]?[A-Z]{1,2}[-\s]?\d{4}\b"
    )

    # Cryptocurrency or Financial Account (e.g., Ethereum/Bitcoin/Bank Acct)
    CRYPTO_REGEX = re.compile(r"\b0x[a-fA-F0-9]{38,42}\b")
    ACCOUNT_REGEX = re.compile(r"\b(?:ACCT|ACCOUNT|IBAN|REF)[-:\s]*([A-Z0-9]{8,24})\b", re.IGNORECASE)

    # Common investigative / organization indicators
    ORG_KEYWORDS = {
        "police", "agency", "department", "bank", "hospital", "telecom", "university",
        "corporation", "ltd", "inc", "consortium", "cartel", "cell", "syndicate"
    }

    @classmethod
    def normalize_phone(cls, phone_str: str) -> str:
        """
        Normalize phone number into standard international or 10-digit format.
        e.g. '+91 98765 43210' -> '+919876543210', '9876543210' -> '+919876543210' (if Indian 10-digit).
        """
        digits = re.sub(r"[^\d+]", "", phone_str)
        if digits.startswith("+"):
            return digits
        if len(digits) == 10:
            return f"+91{digits}"
        if len(digits) == 12 and digits.startswith("91"):
            return f"+{digits}"
        return f"+{digits}" if len(digits) > 7 else digits

    @classmethod
    def normalize_email(cls, email_str: str) -> str:
        """Normalize email address to lowercase stripped."""
        return email_str.strip().lower()

    @classmethod
    def normalize_url(cls, url_str: str) -> str:
        """Normalize URL scheme and domain."""
        url = url_str.strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc.lower()}{parsed.path}"

    @classmethod
    def extract_context_snippet(cls, full_text: str, start: int, end: int, window: int = 60) -> str:
        """Extract a clean human-readable sentence or surrounding snippet for explainability."""
        snippet_start = max(0, start - window)
        snippet_end = min(len(full_text), end + window)
        snippet = full_text[snippet_start:snippet_end].replace("\n", " ").strip()
        prefix = "..." if snippet_start > 0 else ""
        suffix = "..." if snippet_end < len(full_text) else ""
        return f"{prefix}{snippet}{suffix}"

    @classmethod
    def extract_entities_from_text(
        cls,
        text: str,
        evidence_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Extract and normalize all domain entities from plain text,
        preserving context and confidence for every extracted item.
        """
        if not text:
            return []

        entities: list[dict[str, Any]] = []
        seen_keys: set[str] = set()

        def _add_entity(kind: str, raw: str, norm: str, start: int, end: int, conf: float):
            dedup_key = f"{kind}:{norm}"
            if dedup_key in seen_keys:
                return
            seen_keys.add(dedup_key)
            context = cls.extract_context_snippet(text, start, end)
            entities.append({
                "type": kind,
                "raw_value": raw,
                "normalized_value": norm,
                "confidence": round(conf, 2),
                "context": context,
                "source_evidence_id": evidence_id,
            })

        # 1. Email Addresses
        for match in cls.EMAIL_REGEX.finditer(text):
            raw = match.group(0)
            norm = cls.normalize_email(raw)
            _add_entity("EMAIL", raw, norm, match.start(), match.end(), 0.98)

        # 2. URLs
        for match in cls.URL_REGEX.finditer(text):
            raw = match.group(0)
            norm = cls.normalize_url(raw)
            _add_entity("URL", raw, norm, match.start(), match.end(), 0.96)

        # 3. Phone Numbers
        for match in cls.PHONE_REGEX.finditer(text):
            raw = match.group(0).strip()
            digits = re.sub(r"\D", "", raw)
            # Filter out dates or short numbers like 2026-08-01
            if len(digits) >= 10 and len(digits) <= 15:
                norm = cls.normalize_phone(raw)
                _add_entity("PHONE", raw, norm, match.start(), match.end(), 0.92)

        # 4. Devices (IMEI, MAC, IP, Vehicle Plates)
        for match in cls.IMEI_REGEX.finditer(text):
            raw = match.group(0)
            _add_entity("DEVICE", raw, f"IMEI:{raw}", match.start(), match.end(), 0.95)

        for match in cls.IP_REGEX.finditer(text):
            raw = match.group(0)
            _add_entity("DEVICE", raw, f"IP:{raw}", match.start(), match.end(), 0.94)

        for match in cls.MAC_REGEX.finditer(text):
            raw = match.group(0)
            _add_entity("DEVICE", raw, f"MAC:{raw.upper()}", match.start(), match.end(), 0.95)

        for match in cls.PLATE_REGEX.finditer(text):
            raw = match.group(0)
            norm = re.sub(r"[\s-]", "", raw).upper()
            _add_entity("DEVICE", raw, f"VEHICLE:{norm}", match.start(), match.end(), 0.90)

        # 5. Accounts / Crypto Wallets
        for match in cls.CRYPTO_REGEX.finditer(text):
            raw = match.group(0)
            _add_entity("ACCOUNT", raw, raw.lower(), match.start(), match.end(), 0.96)

        for match in cls.ACCOUNT_REGEX.finditer(text):
            raw = match.group(1)
            _add_entity("ACCOUNT", raw, raw.upper(), match.start(1), match.end(1), 0.91)

        # 6. Dates & Times
        for match in cls.DATE_REGEX.finditer(text):
            raw = match.group(0)
            _add_entity("DATE", raw, raw, match.start(), match.end(), 0.88)

        for match in cls.TIME_REGEX.finditer(text):
            raw = match.group(0)
            _add_entity("TIME", raw, raw, match.start(), match.end(), 0.88)

        # 7. Named Entities (Persons, Locations, Organizations) via forensic token analysis
        # Matches patterns like "John Mathew", "Alex Mercer", "Marine Drive", "Kochi", "Sony Alpha"
        name_patterns = re.finditer(
            r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b", text
        )
        for m in name_patterns:
            raw = m.group(1).strip()
            lower = raw.lower()
            if any(w in lower for w in ("january", "february", "march", "april", "august", "sunday", "monday", "sha", "case", "page", "file")):
                continue
            # Classify based on location and org keywords
            if any(k in lower for k in ("drive", "road", "street", "kochi", "junction", "tower", "city", "avenue", "beach", "nagar", "colony", "park", "station", "airport", "market")):
                _add_entity("LOCATION", raw, raw, m.start(1), m.end(1), 0.85)
            elif any(k in lower for k in ("bank", "police", "telecom", "agency", "hospital", "unit")):
                _add_entity("ORGANIZATION", raw, raw, m.start(1), m.end(1), 0.86)
            else:
                _add_entity("PERSON", raw, raw, m.start(1), m.end(1), 0.82)

        return entities
