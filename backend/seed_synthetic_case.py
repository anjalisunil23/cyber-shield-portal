"""
Synthetic Demonstration Case Seeder for Cyber Shield.
Generates Case CS-2026-0003 (Missing Child) with multi-source digital evidence
and runs the end-to-end AI intelligence pipeline.
"""

from __future__ import annotations

import datetime
import io
import os
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from PIL import Image, ImageDraw, ImageFont
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.case import Case, CaseAssignment
from app.models.department import Department
from app.models.enums import CasePriority, CaseStatus, TimelineEventType
from app.models.evidence import Evidence
from app.models.note import Note
from app.models.timeline import TimelineEvent
from app.models.user import User, UserRole
from app.services.ai.pipeline import EvidencePipeline
from app.services.storage import get_storage


def create_synthetic_cctv_image() -> bytes:
    """Generate a realistic synthetic CCTV frame with simulated camera overlay."""
    img = Image.new("RGB", (640, 480), color=(25, 30, 40))
    draw = ImageDraw.Draw(img)

    # Draw simulated night street / camera frame
    draw.rectangle([40, 40, 600, 440], outline=(0, 200, 220), width=2)
    draw.line([(320, 230), (320, 250)], fill=(0, 200, 220), width=1)
    draw.line([(310, 240), (330, 240)], fill=(0, 200, 220), width=1)

    # Add text overlay
    draw.text((50, 50), "SURVEILLANCE CAM-04: MARINE DRIVE JUNCTION", fill=(220, 240, 255))
    draw.text((50, 75), "TIMESTAMP: 2026-08-01 20:15:30 UTC", fill=(0, 255, 200))
    draw.text((50, 100), "GPS: 9.981600 N, 76.275800 E (Kochi Marine Drive)", fill=(180, 200, 220))
    draw.text((50, 390), "TARGET VEHICLE DETECTED: KL-07-CD-4921", fill=(255, 200, 50))
    draw.text((50, 415), "CAMERA: Sony Alpha 7 IV (CCTV Junction Feed)", fill=(150, 170, 190))

    # Add forensic EXIF
    exif = img.getexif()
    # Tag 271: Make, Tag 272: Model, Tag 306: DateTime
    exif[271] = "Sony"
    exif[272] = "Alpha 7 IV (Forensic CCTV Cam 04)"
    exif[306] = "2026:08:01 20:15:30"
    exif[36867] = "2026:08:01 20:15:30"

    buf = io.BytesIO()
    img.save(buf, format="JPEG", exif=exif)
    return buf.getvalue()


def seed_case_cs2026_0003(db: Session, actor: User | None = None) -> dict[str, Any]:
    """
    Idempotently create or reset demonstration case CS-2026-0003.
    Populates 5 diverse digital evidence items and executes the full AI intelligence pipeline.
    """
    storage = get_storage()

    # 1. Resolve Actor / Investigator
    if not actor:
        actor = db.query(User).filter(User.role == UserRole.investigator).first()
    if not actor:
        actor = db.query(User).first()
    if not actor:
        raise ValueError("No user available in database to own synthetic case")

    # 2. Check or Create Case CS-2026-0003
    case = db.query(Case).filter(Case.case_number == "CS-2026-0003").first()
    if case:
        # Delete existing evidence and recreate for clean demonstration state
        for ev in list(case.evidence_items):
            try:
                storage.delete(ev.storage_path)
            except Exception:
                pass
            db.delete(ev)
        db.commit()
    else:
        dept = db.query(Department).first()
        case = Case(
            id=uuid4(),
            case_number="CS-2026-0003",
            title="Operation Safe Haven – Missing Child Investigation",
            description=(
                "Urgent investigation into the reported abduction of a minor near Marine Drive, Kochi. "
                "Digital evidence includes CCTV traffic captures, intercepted instant messaging logs, "
                "telecommunication CDR exports, ransom demand documents, and dispatch witness recordings."
            ),
            priority=CasePriority.high,
            status=CaseStatus.open,
            notes="Active task force assigned. Cross-correlation of suspect phone numbers is top investigative priority.",
            created_by_id=actor.id,
            department_id=dept.id if dept else None,
            investigator_lead_id=actor.id,
        )
        db.add(case)
        db.flush()

        # Assignment
        db.add(
            CaseAssignment(
                case_id=case.id,
                user_id=actor.id,
                assigned_by_id=actor.id,
                is_primary=True,
            )
        )
        db.commit()

    case_id_str = str(case.id)

    # 3. Prepare 5 Multi-Source Evidence Payloads
    cctv_bytes = create_synthetic_cctv_image()

    chat_content = (
        "--- WHATSAPP ENCRYPTED CHAT EXPORT ---\n"
        "Investigation Case Reference: CS-2026-0003\n"
        "Export Date: 2026-08-01 23:00:00 UTC\n\n"
        "[2026-08-01 20:25:10] +919876543210: We have secured the child near Marine Drive tower.\n"
        "[2026-08-01 20:26:45] +919876543210: Alex Mercer said the safehouse vehicle is parked at the junction.\n"
        "[2026-08-01 20:30:15] +919123456789: Confirm the registration plate.\n"
        "[2026-08-01 20:31:00] +919876543210: It is KL-07-CD-4921 dark grey sedan.\n"
        "[2026-08-01 20:35:12] +919876543210: Do not use cellular voice. Only send transaction updates to courier.intel@protonmail.com.\n"
        "[2026-08-01 20:45:00] +919123456789: John Mathew is monitoring the police scanner in Kochi.\n"
    ).encode("utf-8")

    cdr_content = (
        "timestamp,caller_number,dialed_number,duration_sec,cell_tower,device_imei\n"
        "2026-08-01 20:10:00,+919876543210,+919123456789,145,Marine Drive Tower 2,864920048192049\n"
        "2026-08-01 20:25:30,+919876543210,+919876543210,45,Marine Drive Tower 2,864920048192049\n"
        "2026-08-01 20:38:15,+919876543210,+919447112233,60,Marine Drive Tower 1,864920048192049\n"
        "2026-08-01 21:05:12,+919876543210,+919123456789,180,Edappally Tower 1,864920048192049\n"
    ).encode("utf-8")

    ransom_content = (
        "CONFIDENTIAL EVIDENCE - RANSOM DEMAND DOCUMENT\n"
        "Case ID: CS-2026-0003\n"
        "Target: Missing Child Safe Haven\n\n"
        "To Family and Cyber Shield Investigators:\n"
        "We have the child. Transfer 5.5 Bitcoin to wallet 0x71C84941E67fEB46a6fF8f5F9E9B011234567890 within 24 hours.\n"
        "Do not notify the police or attempt wire transfers.\n"
        "Any communication attempt to trace our location will result in immediate consequences.\n"
        "Direct proof of compliance to courier.intel@protonmail.com or contact +919876543210.\n"
        "Deadline: August 2, 2026, 18:00 UTC.\n"
        "Author: Shadow Syndicate Cell\n"
    ).encode("utf-8")

    interview_content = (
        "--- POLICE DISPATCH AUDIO RECORDING (FORENSIC SIDECAR TRANSCRIPT) ---\n"
        "Evidence ID: AUDIO-INTERVIEW-001\n"
        "Case: CS-2026-0003 (Missing Child)\n"
        "Recorded At: 2026-08-01 21:50:00\n\n"
        "[00:00:05] OFFICER: Officer Davis conducting recorded dispatch interview at Marine Drive.\n"
        "[00:00:18] WITNESS: I was walking past Marine Drive promenade at around 8:15 PM.\n"
        "[00:00:32] WITNESS: A dark vehicle with registration KL-07-CD-4921 sped away towards the junction.\n"
        "[00:00:48] WITNESS: I heard a man shout into his phone '+919876543210, we have the child, move now!'.\n"
        "[00:01:05] OFFICER: Did you recognize the individual or see any other suspect?\n"
        "[00:01:15] WITNESS: He mentioned meeting Alex Mercer and John Mathew at Edappally.\n"
        "[00:01:30] OFFICER: Statement concluded. Dispatch alerted for suspect vehicle KL-07-CD-4921.\n"
    ).encode("utf-8")

    evidence_specs = [
        ("EV-01_cctv_junction_frame.jpg", cctv_bytes, "image", "image/jpeg", "CCTV traffic surveillance frame showing target vehicle KL-07-CD-4921 at Marine Drive junction"),
        ("EV-02_whatsapp_intercept_chat.txt", chat_content, "chat_export", "text/plain", "Encrypted messaging platform export between suspects discussing abduction logistics"),
        ("EV-03_telecom_call_detail_record.csv", cdr_content, "call_log", "text/csv", "Carrier Call Detail Record (CDR) spreadsheet with IMEI and cellular tower locations"),
        ("EV-04_ransom_demand_note.txt", ransom_content, "document", "text/plain", "Physical / digital ransom extortion note demanding cryptocurrency payment"),
        ("EV-05_police_dispatch_interview.txt", interview_content, "audio", "audio/wav", "Police dispatch recorded witness interview regarding Marine Drive abduction"),
    ]

    # 4. Save and Register Evidence
    created_evidence_ids = []
    for orig_name, file_bytes, ftype, mtype, desc in evidence_specs:
        storage_path, sha256 = storage.save(case_id=case_id_str, filename=orig_name, data=file_bytes)
        ev = Evidence(
            id=uuid4(),
            case_id=case.id,
            filename=Path(storage_path).name,
            original_name=orig_name,
            file_type=ftype,
            mime_type=mtype,
            file_size=len(file_bytes),
            storage_path=storage_path,
            sha256_hash=sha256,
            description=desc,
            tags=["synthetic_demo", "missing_child", ftype],
            uploaded_by_id=actor.id,
            is_duplicate=False,
        )
        db.add(ev)
        db.flush()
        created_evidence_ids.append(ev.id)

    # 5. Add Initial Investigator Note
    db.add(
        Note(
            id=uuid4(),
            case_id=case.id,
            author_id=actor.id,
            title="Initial Abduction Triage",
            body=(
                "Received emergency missing child report. Ingested 5 critical evidence sources. "
                "Immediate priority is automated entity extraction and cross-source phone/vehicle correlation."
            ),
            is_pinned=True,
        )
    )

    # 6. Add Case Created Timeline Event
    db.add(
        TimelineEvent(
            id=uuid4(),
            case_id=case.id,
            event_type=TimelineEventType.case_created,
            title="Case CS-2026-0003 Opened",
            description="High-priority missing child investigation initiated.",
            created_by_id=actor.id,
            event_at=datetime.datetime(2026, 8, 1, 20, 0, 0, tzinfo=datetime.timezone.utc),
        )
    )

    db.commit()

    # 7. Execute End-to-End AI Intelligence Pipeline
    pipeline = EvidencePipeline(db)
    pipeline_result = pipeline.run_case_pipeline(case.id, actor_id=actor.id)

    return {
        "success": True,
        "case_id": case_id_str,
        "case_number": case.case_number,
        "title": case.title,
        "evidence_count": len(created_evidence_ids),
        "pipeline_result": pipeline_result,
    }


if __name__ == "__main__":
    db_gen = get_db()
    session = next(db_gen)
    try:
        res = seed_case_cs2026_0003(session)
        print("==================================================")
        print("SYNTHETIC CASE SEEDED SUCCESSFULLY:")
        print(f"Case Number: {res['case_number']}")
        print(f"Evidence Files: {res['evidence_count']}")
        print(f"Correlations: {res['pipeline_result'].get('correlations_found')}")
        print(f"Timeline Events: {res['pipeline_result'].get('timeline_events_generated')}")
        print(f"Risk Score: {res['pipeline_result'].get('risk_score')}/100 ({res['pipeline_result'].get('risk_level')})")
        print(f"Leads Generated: {res['pipeline_result'].get('leads_generated')}")
        print("==================================================")
    finally:
        session.close()
