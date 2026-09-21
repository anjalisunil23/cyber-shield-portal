"""Document text extraction for PDF, DOCX, TXT, CSV, EML/email, and structured chat/call logs."""

from __future__ import annotations

import csv
import email
from email import policy
import io
import json
from pathlib import Path
from typing import Any
import zipfile
import xml.etree.ElementTree as ET

try:
    import pypdf
except ImportError:  # pragma: no cover - optional until pip install
    pypdf = None  # type: ignore


class TextService:
    @staticmethod
    def extract_pdf_text(data: bytes) -> str:
        """Extract full text from PDF using pypdf."""
        text_parts: list[str] = []
        if pypdf is None:
            return "[PDF parsing unavailable: install pypdf]"
        try:
            reader = pypdf.PdfReader(io.BytesIO(data))
            for i, page in enumerate(reader.pages):
                extracted = page.extract_text()
                if extracted and extracted.strip():
                    text_parts.append(f"--- [Page {i + 1}] ---\n" + extracted.strip())
        except Exception as e:
            return f"[PDF parsing partial failure: {str(e)}]"
        return "\n\n".join(text_parts)

    @staticmethod
    def extract_docx_text(data: bytes) -> str:
        """Extract text from DOCX using zipfile and word/document.xml (zero extra heavy dependencies)."""
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as docx:
                xml_content = docx.read("word/document.xml")
                root = ET.fromstring(xml_content)
                # WordprocessingML namespace
                namespaces = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
                paragraphs = []
                for p in root.findall(".//w:p", namespaces):
                    p_text = "".join(node.text for node in p.findall(".//w:t", namespaces) if node.text)
                    if p_text.strip():
                        paragraphs.append(p_text.strip())
                return "\n".join(paragraphs)
        except Exception as e:
            return f"[DOCX parsing error: {str(e)}]"

    @staticmethod
    def extract_email_text(data: bytes) -> str:
        """Extract headers, sender, recipient, subject, and body from RFC822 .eml message."""
        try:
            msg = email.message_from_bytes(data, policy=policy.default)
            headers = [
                f"From: {msg.get('From', 'Unknown')}",
                f"To: {msg.get('To', 'Unknown')}",
                f"Date: {msg.get('Date', 'Unknown')}",
                f"Subject: {msg.get('Subject', 'No Subject')}",
            ]
            body_parts = []
            if msg.is_multipart():
                for part in msg.walk():
                    ctype = part.get_content_type()
                    cdispo = str(part.get("Content-Disposition"))
                    if ctype == "text/plain" and "attachment" not in cdispo:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body_parts.append(payload.decode(errors="replace"))
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    body_parts.append(payload.decode(errors="replace"))
                else:
                    body_parts.append(str(msg.get_payload() or ""))

            full_body = "\n".join(body_parts).strip()
            return "\n".join(headers) + "\n\n--- Email Body ---\n" + (full_body or "[No text body found]")
        except Exception as e:
            return f"[Email parsing error: {str(e)}]"

    @staticmethod
    def extract_csv_text(data: bytes) -> str:
        """Extract structured records from CSV into human and entity-readable lines."""
        try:
            content = data.decode(errors="replace")
            reader = csv.reader(io.StringIO(content))
            lines: list[str] = []
            headers: list[str] = []
            for idx, row in enumerate(reader):
                if idx == 0:
                    headers = row
                    lines.append("CSV Columns: " + ", ".join(headers))
                else:
                    if headers and len(row) <= len(headers):
                        formatted = " | ".join(f"{h}: {val}" for h, val in zip(headers, row) if val.strip())
                        lines.append(f"Row {idx}: {formatted}")
                    else:
                        lines.append(f"Row {idx}: " + " | ".join(row))
            return "\n".join(lines)
        except Exception as e:
            return f"[CSV parsing error: {str(e)}]"

    @staticmethod
    def extract_json_text(data: bytes) -> str:
        """Extract text and key fields from structured JSON exports."""
        try:
            parsed = json.loads(data.decode(errors="replace"))
            return json.dumps(parsed, indent=2, ensure_ascii=False)
        except Exception:
            return data.decode(errors="replace")

    @classmethod
    def extract_text_from_bytes(
        cls,
        data: bytes,
        filename: str,
        file_type: str,
        mime_type: str | None,
    ) -> str:
        """Dispatch to appropriate text extraction engine based on extension and mime type."""
        ext = Path(filename).suffix.lower()
        mime = (mime_type or "").lower()

        if ext == ".pdf" or mime == "application/pdf":
            return cls.extract_pdf_text(data)

        if ext in (".docx", ".doc"):
            return cls.extract_docx_text(data)

        if ext in (".eml", ".msg") or mime.startswith("message/"):
            return cls.extract_email_text(data)

        if ext in (".csv", ".tsv"):
            return cls.extract_csv_text(data)

        if ext in (".json", ".jsonl"):
            return cls.extract_json_text(data)

        if ext in (".txt", ".log", ".md", ".rtf", ".gpx", ".kml", ".html", ".htm"):
            return data.decode(errors="replace")

        # For unknown text-like files, try decoding utf-8
        try:
            decoded = data.decode("utf-8")
            if decoded and sum(c.isprintable() or c in "\r\n\t" for c in decoded) / len(decoded) > 0.85:
                return decoded
        except Exception:
            pass

        return ""
