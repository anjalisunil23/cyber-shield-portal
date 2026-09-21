"""Theme-aware synthetic evidence payloads with intentional cross-source correlation."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from dataclasses import dataclass
from typing import Any

from app.models.case import Case
from app.services.repository.file_factory import (
    WATERMARK,
    build_docx,
    build_map_image,
    build_ocr_image,
    build_pdf,
    build_video,
    build_wav,
    try_tts_wav,
)


@dataclass
class GeneratedFile:
    filename: str
    category: str
    file_type: str
    mime_type: str
    description: str
    data: bytes
    tags: list[str]
    entities: list[str]


def detect_theme(case: Case) -> str:
    blob = f"{case.title or ''} {case.description or ''} {case.notes or ''} {case.case_number}".lower()
    if any(k in blob for k in ("missing", "child", "abduct", "kidnap", "safe haven")):
        return "missing_person"
    if any(k in blob for k in ("fraud", "invoice", "wire", "phishing", "bank", "mule")):
        return "fraud"
    if any(k in blob for k in ("cyber", "malware", "ransom", "hack", "intrusion", "ddos")):
        return "cybercrime"
    return "general"


def persona_for_case(case: Case) -> dict[str, str]:
    if case.case_number == "CS-2026-0003" or detect_theme(case) == "missing_person":
        return {
            "person": "Alex Mercer",
            "person_b": "John Mathew",
            "phone": "+919876543210",
            "phone_b": "+919123456789",
            "email": "courier.intel@cybershield.test",
            "org": "Shadow Syndicate Cell",
            "location": "Marine Drive, Kochi",
            "location_b": "Edappally Junction",
            "device": "IMEI:864920048192049",
            "plate": "KL-07-CD-4921",
            "date": "2026-08-01",
            "time": "20:30:15",
            "lat": "9.981600",
            "lon": "76.275800",
        }
    digest = hashlib.md5(case.case_number.encode("utf-8")).hexdigest()
    n = int(digest[:6], 16)
    first = ["Ravi", "Meera", "Arjun", "Nina", "Kabir", "Lila", "Omar", "Priya"][n % 8]
    last = ["Shah", "Nair", "Khan", "D'Souza", "Iyer", "Fernandes", "Patel", "Das"][(n // 8) % 8]
    city = ["Pune", "Hyderabad", "Bengaluru", "Jaipur", "Chennai", "Ahmedabad"][n % 6]
    street = ["Lake View Road", "Station Road", "Tech Park Gate", "Harbour Lane"][(n // 3) % 4]
    phone_core = f"{7000000000 + (n % 99999999):010d}"
    return {
        "person": f"{first} {last}",
        "person_b": f"{['Samir', 'Anita', 'Dev', 'Tara'][n % 4]} {['Rao', 'Menon', 'Gupta', 'Bose'][n % 4]}",
        "phone": f"+91{phone_core}",
        "phone_b": f"+91{int(phone_core) + 17}",
        "email": f"{first.lower()}.{last.lower().replace(chr(39), '')}@cybershield.test",
        "org": ["Northwind Logistics Ltd", "Cedar Packet Labs", "Helios Payments", "Orion Mesh"][n % 4],
        "location": f"{street}, {city}",
        "location_b": f"Warehouse 7, {city}",
        "device": f"IMEI:35{n % 10}92004{n % 100000:05d}",
        "plate": f"{['MH', 'KA', 'TN', 'GJ'][n % 4]}-{12 + n % 20:02d}-AB-{(n % 9000) + 1000}",
        "date": f"2026-07-{(n % 27) + 1:02d}",
        "time": f"{10 + (n % 10):02d}:{(n % 50):02d}:00",
        "lat": f"{12 + (n % 12)}.{(n % 900000):06d}",
        "lon": f"{72 + (n % 10)}.{(n % 800000):06d}",
    }


def _csv(rows: list[list[str]]) -> bytes:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerows(rows)
    return (WATERMARK + "\n" + buf.getvalue()).encode("utf-8")


def build_dataset(case: Case, selected: set[str] | None = None, include_duplicate: bool = False) -> list[GeneratedFile]:
    theme = detect_theme(case)
    p = persona_for_case(case)
    selected = selected or {
        "documents",
        "images",
        "audio",
        "video",
        "communications",
        "location",
        "browser",
        "call_logs",
        "social_export",
    }
    files: list[GeneratedFile] = []
    cn = case.case_number
    title = case.title

    def add(item: GeneratedFile, group: str) -> None:
        if group in selected:
            files.append(item)

    notes = (
        f"{WATERMARK}\nCase: {cn} — {title}\nTheme: {theme}\n\n"
        f"Investigator note (fictional): {p['person']} contacted {p['person_b']} at {p['time']} on {p['date']}. "
        f"Phone {p['phone']} and email {p['email']} appear in intercepts. "
        f"Device {p['device']} was last seen near {p['location']} ({p['lat']}, {p['lon']}). "
        f"Vehicle {p['plate']} is associated with {p['org']}.\n"
    )
    add(
        GeneratedFile(
            "investigator_notes.txt",
            "documents",
            "document",
            "text/plain",
            "Synthetic investigator notes linking person, phone, and location",
            notes.encode("utf-8"),
            ["notes", "synthetic"],
            [p["person"], p["phone"], p["location"]],
        ),
        "documents",
    )

    add(
        GeneratedFile(
            "witness_statement.pdf",
            "documents",
            "document",
            "application/pdf",
            "Synthetic witness statement PDF",
            build_pdf(
                f"Witness Statement — {cn}",
                [
                    WATERMARK,
                    f"Witness reported seeing {p['person']} near {p['location']} at {p['time']} on {p['date']}.",
                    f"A call was placed to {p['phone']} and a message mentioned {p['email']}.",
                    f"Vehicle {p['plate']} departed toward {p['location_b']}.",
                    "This statement is fictional demonstration data only.",
                ],
            ),
            ["statement", "synthetic"],
            [p["person"], p["phone"], p["plate"]],
        ),
        "documents",
    )

    add(
        GeneratedFile(
            "case_report.docx",
            "documents",
            "document",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "Synthetic DOCX investigation report",
            build_docx(
                f"Investigation Report {cn}",
                [
                    WATERMARK,
                    f"Subject {p['person']} of {p['org']} is referenced across chat, email, and call records.",
                    f"Normalized phone {p['phone']} should match intercepts and CDR rows.",
                    f"Timeline anchor: {p['date']} {p['time']} at {p['location']}.",
                    "AI findings from this file are recommendations only.",
                ],
            ),
            ["report", "synthetic"],
            [p["person"], p["org"], p["phone"]],
        ),
        "documents",
    )

    summary = {
        "synthetic": True,
        "dataset": "CYBER_SHIELD_DEMO",
        "case_number": cn,
        "theme": theme,
        "entities": p,
        "disclaimer": WATERMARK,
    }
    add(
        GeneratedFile(
            "evidence_summary.json",
            "documents",
            "document",
            "application/json",
            "Structured synthetic evidence summary",
            json.dumps(summary, indent=2).encode("utf-8"),
            ["summary", "synthetic"],
            [p["person"], p["email"]],
        ),
        "documents",
    )

    add(
        GeneratedFile(
            "timeline_report.txt",
            "documents",
            "document",
            "text/plain",
            "Synthetic timeline report matching chat, CDR, and GPS timestamps",
            (
                f"{WATERMARK}\nTIMELINE REPORT {cn}\n"
                f"{p['date']} {p['time']}  {p['person']} at {p['location']} ({p['lat']}, {p['lon']})\n"
                f"{p['date']} {p['time']}  Call {p['phone']} -> {p['phone_b']}\n"
                f"{p['date']} 20:35:00  Email {p['email']} referenced {p['org']}\n"
                f"{p['date']} 20:41:00  Device {p['device']} near {p['location_b']}\n"
            ).encode("utf-8"),
            ["timeline", "synthetic"],
            [p["person"], p["phone"], p["location"]],
        ),
        "documents",
    )

    chat = (
        f"{WATERMARK}\n--- SYNTHETIC CHAT EXPORT ---\nCase: {cn}\n"
        f"[{p['date']} {p['time']}] {p['phone']}: {p['person']} is at {p['location']}. Vehicle {p['plate']}.\n"
        f"[{p['date']} 20:35:00] {p['phone_b']}: Confirm with {p['email']} and {p['person_b']}.\n"
        f"[{p['date']} 20:41:00] {p['phone']}: Device {p['device']} stays offline after {p['location_b']}.\n"
    )
    add(
        GeneratedFile(
            "chat_export.txt",
            "communications",
            "chat_export",
            "text/plain",
            "Synthetic chat export with shared phone and person",
            chat.encode("utf-8"),
            ["chat", "synthetic"],
            [p["person"], p["phone"], p["plate"]],
        ),
        "communications",
    )

    email = (
        f"From: {p['email']}\nTo: investigator@cybershield.test\nDate: {p['date']} {p['time']}\n"
        f"Subject: [SYNTHETIC] Coordination note for {cn}\n\n"
        f"{WATERMARK}\n{p['person']} requested contact via {p['phone']}. Meeting at {p['location']}.\n"
        f"CC reference: {p['person_b']} / {p['org']}.\n"
    )
    add(
        GeneratedFile(
            "email_export.eml",
            "communications",
            "chat_export",
            "message/rfc822",
            "Synthetic email using .test domain",
            email.encode("utf-8"),
            ["email", "synthetic"],
            [p["email"], p["person"], p["phone"]],
        ),
        "communications",
    )

    sms = {
        "synthetic": True,
        "disclaimer": WATERMARK,
        "messages": [
            {
                "at": f"{p['date']} {p['time']}",
                "from": p["phone"],
                "to": p["phone_b"],
                "text": f"{p['person']} arriving {p['location']}",
            }
        ],
    }
    add(
        GeneratedFile(
            "sms_export.json",
            "communications",
            "chat_export",
            "application/json",
            "Synthetic SMS export",
            json.dumps(sms, indent=2).encode("utf-8"),
            ["sms", "synthetic"],
            [p["phone"], p["person"]],
        ),
        "communications",
    )
    social = {
        "synthetic": True,
        "disclaimer": WATERMARK,
        "platform": "cybershield.test",
        "profile": p["person"],
        "posts": [
            {
                "at": f"{p['date']} {p['time']}",
                "text": f"Seen near {p['location']}. Contact {p['email']}.",
            }
        ],
    }
    add(
        GeneratedFile(
            "social_export.json",
            "social_export",
            "chat_export",
            "application/json",
            "Synthetic social-media export",
            json.dumps(social, indent=2).encode("utf-8"),
            ["social", "synthetic"],
            [p["person"], p["email"]],
        ),
        "social_export",
    )

    call_rows = [
        ["timestamp", "caller_number", "dialed_number", "duration_sec", "cell_tower", "device_imei"],
        [f"{p['date']} {p['time']}", p["phone"], p["phone_b"], "145", p["location"], p["device"].replace("IMEI:", "")],
        [f"{p['date']} 20:41:00", p["phone_b"], p["phone"], "60", p["location_b"], p["device"].replace("IMEI:", "")],
    ]
    add(
        GeneratedFile(
            "call_log.csv",
            "call_logs",
            "call_log",
            "text/csv",
            "Synthetic call detail record",
            _csv(call_rows),
            ["cdr", "synthetic"],
            [p["phone"], p["device"]],
        ),
        "call_logs" if "call_logs" in selected else "communications",
    )

    gps_rows = [
        ["timestamp", "latitude", "longitude", "label", "related_phone"],
        [f"{p['date']} {p['time']}", p["lat"], p["lon"], p["location"], p["phone"]],
        [f"{p['date']} 20:45:00", p["lat"], p["lon"], p["location_b"], p["phone"]],
    ]
    add(
        GeneratedFile(
            "gps_history.csv",
            "location",
            "document",
            "text/csv",
            "Synthetic GPS trail matching chat timestamps",
            _csv(gps_rows),
            ["gps", "synthetic"],
            [p["location"], p["phone"]],
        ),
        "location",
    )
    loc_json = {
        "synthetic": True,
        "disclaimer": WATERMARK,
        "history": [
            {"at": f"{p['date']} {p['time']}", "place": p["location"], "lat": p["lat"], "lon": p["lon"], "person": p["person"]}
        ],
    }
    add(
        GeneratedFile(
            "location_history.json",
            "location",
            "document",
            "application/json",
            "Synthetic location history JSON",
            json.dumps(loc_json, indent=2).encode("utf-8"),
            ["location", "synthetic"],
            [p["person"], p["location"]],
        ),
        "location",
    )

    add(
        GeneratedFile(
            "ocr_investigator_note.png",
            "images",
            "image",
            "image/png",
            "OCR-readable synthetic investigator note image",
            build_ocr_image(
                f"{cn} INVESTIGATOR NOTE",
                [
                    WATERMARK,
                    f"Person: {p['person']}",
                    f"Phone: {p['phone']}",
                    f"Email: {p['email']}",
                    f"Location: {p['location']}",
                    f"When: {p['date']} {p['time']}",
                    f"Vehicle: {p['plate']}",
                    f"Device: {p['device']}",
                ],
            ),
            ["ocr", "synthetic"],
            [p["person"], p["phone"]],
        ),
        "images",
    )
    add(
        GeneratedFile(
            "chat_screenshot.png",
            "images",
            "image",
            "image/png",
            "Synthetic chat screenshot for OCR",
            build_ocr_image(
                "SYNTHETIC MESSAGE SCREENSHOT",
                [
                    f"{p['phone']}: {p['person']} at {p['location']}",
                    f"{p['phone_b']}: Use {p['email']} only",
                    f"Vehicle {p['plate']} mentioned",
                    WATERMARK,
                ],
            ),
            ["screenshot", "synthetic"],
            [p["person"], p["email"]],
        ),
        "images",
    )
    add(
        GeneratedFile(
            "map_placeholder.jpg",
            "images",
            "image",
            "image/jpeg",
            "Synthetic map/location image",
            build_map_image(p["location"], p["lat"], p["lon"], f"{p['person']} event at {p['time']}"),
            ["map", "synthetic"],
            [p["location"]],
        ),
        "images",
    )

    spoken = (
        f"Synthetic audio note for case {cn}. {p['person']} used phone {p['phone']} at {p['location']} "
        f"on {p['date']} at {p['time']}."
    )
    audio = try_tts_wav(spoken) or build_wav()
    add(
        GeneratedFile(
            "investigator_audio_note.wav",
            "audio",
            "audio",
            "audio/wav",
            "Synthetic audio note (tone or local TTS). Transcript stored as companion text.",
            audio,
            ["audio", "synthetic"],
            [p["person"], p["phone"]],
        ),
        "audio",
    )
    transcript = (
        f"{WATERMARK}\nTRANSCRIPT:\nSPEAKER: Investigator (synthetic)\n"
        f"[00:00:02] {spoken}\n[00:00:08] Contact {p['email']} and {p['person_b']}.\n"
    )
    add(
        GeneratedFile(
            "investigator_audio_transcript.txt",
            "audio",
            "document",
            "text/plain",
            "Fallback transcript for synthetic audio (does not claim Whisper ran)",
            transcript.encode("utf-8"),
            ["transcript", "synthetic"],
            [p["person"], p["email"]],
        ),
        "audio",
    )

    video_bytes, ext, mime = build_video(
        [f"{cn} {theme}", f"{p['person']} {p['phone']}", p["location"], WATERMARK],
        seconds=6,
    )
    vtype = "video" if ext == ".mp4" else "image"
    add(
        GeneratedFile(
            f"briefing{ext}",
            "video",
            vtype,
            mime,
            "Synthetic briefing clip (MP4 when ffmpeg is available, otherwise GIF)",
            video_bytes,
            ["video", "synthetic"],
            [p["person"], p["location"]],
        ),
        "video",
    )

    if theme in {"cybercrime", "fraud", "general"}:
        browser = [
            ["visited_at", "url", "title", "account"],
            [f"{p['date']} 09:12:00", "https://mail.cybershield.test/inbox", "Mail", p["email"]],
            [f"{p['date']} 09:18:00", "https://payments.cybershield.test/transfer", "Transfer", p["person"]],
        ]
        add(
            GeneratedFile(
                "browser_history.csv",
                "browser",
                "document",
                "text/csv",
                "Synthetic browser history",
                _csv(browser),
                ["browser", "synthetic"],
                [p["email"], p["person"]],
            ),
            "browser" if "browser" in selected else "communications",
        )

    if theme == "fraud":
        tx = [
            ["timestamp", "account", "amount", "counterparty", "note"],
            [f"{p['date']} {p['time']}", "ACCT-88421", "420000", p["org"], f"Contact {p['phone']}"],
            [f"{p['date']} 21:00:00", "ACCT-88421", "15000", p["person"], "synthetic split"],
        ]
        add(
            GeneratedFile(
                "transactions.csv",
                "documents",
                "document",
                "text/csv",
                "Synthetic transaction ledger",
                _csv(tx),
                ["fraud", "synthetic"],
                [p["org"], p["phone"]],
            ),
            "documents",
        )
        add(
            GeneratedFile(
                "invoice.pdf",
                "documents",
                "document",
                "application/pdf",
                "Synthetic invoice PDF",
                build_pdf(
                    f"Invoice — {p['org']}",
                    [WATERMARK, f"Bill to {p['person']}", f"Phone {p['phone']}", f"Email {p['email']}", "Amount 420000 (synthetic)"],
                ),
                ["invoice", "synthetic"],
                [p["person"], p["email"]],
            ),
            "documents",
        )

    if theme == "cybercrime":
        logs = {
            "synthetic": True,
            "disclaimer": WATERMARK,
            "logins": [
                {"at": f"{p['date']} 08:01:00", "account": p["email"], "ip": "203.0.113.44", "device": p["device"]}
            ],
        }
        add(
            GeneratedFile(
                "login_records.json",
                "documents",
                "document",
                "application/json",
                "Synthetic login records",
                json.dumps(logs, indent=2).encode("utf-8"),
                ["cyber", "synthetic"],
                [p["email"], p["device"]],
            ),
            "documents",
        )

    manifest = {
        "synthetic": True,
        "dataset": "CYBER_SHIELD_DEMO",
        "source": "synthetic_evidence_generator",
        "case_number": cn,
        "theme": theme,
        "disclaimer": WATERMARK,
        "files": [f.filename for f in files],
    }
    add(
        GeneratedFile(
            "dataset_manifest.json",
            "metadata",
            "document",
            "application/json",
            "Repository manifest for this synthetic dataset",
            json.dumps(manifest, indent=2).encode("utf-8"),
            ["manifest", "synthetic"],
            [],
        ),
        "documents",
    )

    if include_duplicate:
        original = next((f for f in files if f.filename == "investigator_notes.txt"), None)
        if original:
            files.append(
                GeneratedFile(
                    "investigator_notes_duplicate.txt",
                    "documents",
                    "document",
                    "text/plain",
                    "Intentional duplicate of investigator_notes.txt (identical SHA-256)",
                    original.data,
                    ["duplicate", "synthetic"],
                    original.entities,
                )
            )

    # Deduplicate accidental double-add of sms for social_export
    seen: set[str] = set()
    unique: list[GeneratedFile] = []
    for f in files:
        if f.filename in seen:
            continue
        seen.add(f.filename)
        unique.append(f)
    return unique
