"""
Master Synthetic Evidence Seeder for Cyber Shield.
Populates rich, multimodal digital evidence files for ALL existing cases in the database,
and executes the full AI intelligence pipeline (Metadata, OCR, Speech, Entities, Correlations, Risk, Leads).
"""

from __future__ import annotations

import datetime
import io
import os
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from PIL import Image, ImageDraw
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.case import Case, CaseAssignment
from app.models.enums import CasePriority, CaseStatus, TimelineEventType
from app.models.evidence import Evidence
from app.models.note import Note
from app.models.timeline import TimelineEvent
from app.models.user import User, UserRole
from app.services.ai.pipeline import EvidencePipeline
from app.services.storage import get_storage


def create_forensic_image(
    title: str,
    subtitle: str,
    location_str: str,
    camera_make: str = "Sony",
    camera_model: str = "Alpha 7 IV (Forensic Cam)",
    date_str: str = "2026:08:10 14:30:00",
    lat: float = 19.0760,
    lon: float = 72.8777,
) -> bytes:
    """Generate a realistic synthetic evidence JPEG with valid forensic EXIF metadata."""
    img = Image.new("RGB", (640, 480), color=(20, 24, 32))
    draw = ImageDraw.Draw(img)

    # Frame border & crosshairs
    draw.rectangle([30, 30, 610, 450], outline=(0, 180, 216), width=2)
    draw.line([(320, 220), (320, 260)], fill=(0, 180, 216), width=1)
    draw.line([(300, 240), (340, 240)], fill=(0, 180, 216), width=1)

    # Text overlays
    draw.text((45, 45), f"CYBERSHIELD DIGITAL FORENSIC CAPTURE // {title.upper()}", fill=(240, 245, 255))
    draw.text((45, 70), f"REF: {subtitle}", fill=(0, 230, 180))
    draw.text((45, 95), f"TIMESTAMP: {date_str.replace(':', '-', 2)} UTC", fill=(180, 200, 220))
    draw.text((45, 120), f"GPS TELEMETRY: {lat:.4f} N, {lon:.4f} E ({location_str})", fill=(255, 200, 80))
    draw.text((45, 400), f"OPTICAL HARDWARE: {camera_make} {camera_model}", fill=(160, 180, 200))
    draw.text((45, 420), "STATUS: CRYPTOGRAPHICALLY SECURED EVIDENCE", fill=(100, 220, 100))

    # Standard EXIF tags
    exif = img.getexif()
    exif[271] = camera_make
    exif[272] = camera_model
    exif[306] = date_str
    exif[36867] = date_str

    buf = io.BytesIO()
    img.save(buf, format="JPEG", exif=exif)
    return buf.getvalue()


# Evidence Specs Generator for each case type
def get_case_evidence_specs(case: Case) -> list[tuple[str, bytes, str, str, str]]:
    num = case.case_number
    title = case.title or ""

    # 1. CS-2026-0001: Messaging Fraud
    if "0001" in num or "messaging fraud" in title.lower():
        cctv = create_forensic_image(
            title="SURVEILLANCE CAM-02: BANKING HUB",
            subtitle="Suspect ATM Cash Extraction",
            location_str="Bandra Kurla Complex, Mumbai",
            camera_make="Axis Communications",
            camera_model="P1455-LE Network Camera",
            date_str="2026:07:15 11:24:18",
            lat=19.0664,
            lon=72.8687,
        )
        chat = (
            "--- WHATSAPP ENCRYPTED CHAT EXPORT ---\n"
            "Case Reference: CS-2026-0001 (Cross-border Messaging Fraud)\n"
            "Export Date: 2026-07-16 08:30:00 UTC\n\n"
            "[2026-07-15 10:15:00] +971501234567: Did the corporate CFO authorize the $420,000 wire to DBS Bank Singapore?\n"
            "[2026-07-15 10:16:30] +919820123456: Yes, the invoice spoofing worked. Account number is 003-902-1142.\n"
            "[2026-07-15 10:20:00] +971501234567: Tell Dmitry to split the funds immediately via USDT to 0x71C84941E67fEB46a6fF8f5F9E9B011234567890.\n"
            "[2026-07-15 10:25:12] +919820123456: Understood. Our courier in Mumbai at Bandra Kurla Complex is ready.\n"
            "[2026-07-15 10:30:00] +971501234567: Send transaction proof only to finance.wire@consultant-group.org.\n"
        ).encode("utf-8")

        cdr = (
            "timestamp,caller_number,dialed_number,duration_sec,cell_tower,device_imei\n"
            "2026-07-15 10:12:00,+971501234567,+919820123456,190,BKC Mumbai Tower 1,358920048192011\n"
            "2026-07-15 10:22:30,+919820123456,+971501234567,110,BKC Mumbai Tower 2,358920048192011\n"
            "2026-07-15 11:05:14,+919820123456,+919811223344,45,Nariman Point Tower,864920048192049\n"
            "2026-07-15 11:40:00,+971501234567,+6581234567,310,Singapore Changi Roaming,358920048192011\n"
        ).encode("utf-8")

        phish = (
            "INTERCEPTED PHISHING EMAIL HEADERS & BODY\n"
            "Case: CS-2026-0001\n"
            "Received: from mail.wire-security-update.com (185.220.101.5)\n"
            "From: cfo@cyber-shield-corp.com\n"
            "To: treasury.ops@cyber-shield-corp.com\n"
            "Subject: URGENT: Q3 Vendor Settlement Wire Transfer Required\n\n"
            "Please process immediate SWIFT wire of $420,000 USD to our overseas partner DBS Bank Singapore.\n"
            "Account: 003-902-1142 | Beneficiary: Global Consulting Partners Ltd.\n"
            "Contact phone for authorization: +971501234567.\n"
        ).encode("utf-8")

        interview = (
            "--- MONEY MULE AUDIO INTERROGATION TRANSCRIPT ---\n"
            "Recorded At: Mumbai Cyber Crime Cell\n"
            "Officer: Inspector R. Sen | Suspect: Rahul V. (Account Holder)\n\n"
            "[00:00:10] OFFICER: Who instructed you to open the current account at DBS Bank and receive +971501234567 calls?\n"
            "[00:00:25] SUSPECT: A man named Dmitry contacted me on Telegram. He said he would pay 5% commission.\n"
            "[00:00:42] OFFICER: Where did you hand over the cash?\n"
            "[00:00:55] SUSPECT: At Bandra Kurla Complex near the coffee shop. He was driving a dark sedan.\n"
            "[00:01:10] OFFICER: Did he provide an email address?\n"
            "[00:01:18] SUSPECT: Yes, finance.wire@consultant-group.org.\n"
        ).encode("utf-8")

        return [
            ("EV-01_whatsapp_fraud_intercept.txt", chat, "chat_export", "text/plain", "Encrypted WhatsApp chat organizing $420,000 corporate wire fraud"),
            ("EV-02_suspect_atm_cctv_frame.jpg", cctv, "image", "image/jpeg", "Forensic CCTV surveillance capture of suspect mule at BKC ATM"),
            ("EV-03_telecom_roaming_cdr.csv", cdr, "call_log", "text/csv", "Carrier Call Detail Record linking UAE caller +971501234567 to Mumbai mule"),
            ("EV-04_phishing_email_headers.txt", phish, "document", "text/plain", "Spoofed executive email headers and wire instructions"),
            ("EV-05_mule_interrogation_transcript.txt", interview, "audio", "audio/wav", "Recorded police interrogation transcript of beneficiary account mule"),
        ]

    # 2. CS-2026-0002: Encrypted Storage Drive
    elif "0002" in num or "encrypted storage" in title.lower():
        photo = create_forensic_image(
            title="FORENSIC LAB SEIZURE // ENCRYPTED SSD",
            subtitle="Western Digital Black NVMe 2TB",
            location_str="Safehouse Lab 04, Kochi",
            camera_make="Nikon",
            camera_model="D850 Digital SLR",
            date_str="2026:07:22 03:14:22",
            lat=9.9312,
            lon=76.2673,
        )
        autopsy = (
            "AUTOPSY / ENCASE FORENSIC DRIVE EXTRACTION REPORT\n"
            "Drive Serial: WDC-WDS200T3X0E-001920\n"
            "SHA-256 Physical Image: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855\n"
            "File System: NTFS / BitLocker Encrypted Partition (Recovered)\n\n"
            "Recovered Files Summary:\n"
            "1. /Users/Phantom/telegram_desktop/tdata/messages.sqlite (24.2 MB)\n"
            "2. /Users/Phantom/Documents/cold_wallet_seed.txt (Recovered via Carving)\n"
            "3. /Users/Phantom/AppData/Roaming/Electrum/wallets/default_wallet\n"
            "Primary User Account: phantom_operator@protonmail.com\n"
            "Suspect IP Address logged in session: 103.21.244.18\n"
        ).encode("utf-8")

        tg_chat = (
            "--- DECRYPTED TELEGRAM CHAT LOGS ---\n"
            "Recovered from seized SSD SQLite database.\n\n"
            "[2026-07-20 22:15:10] @phantom_operator: The hardware wallet seed is split across the cloud backup.\n"
            "[2026-07-20 22:18:00] @crypto_vault: Send the destination Bitcoin address for the payoff.\n"
            "[2026-07-20 22:20:45] @phantom_operator: Deposit 12.5 BTC to 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa.\n"
            "[2026-07-20 22:22:10] @phantom_operator: If police arrive at Kochi safehouse, trigger the remote kill switch on +919876543210.\n"
            "[2026-07-20 22:35:00] @crypto_vault: Alex Mercer confirmed delivery of the encrypted drive.\n"
        ).encode("utf-8")

        ledger = (
            "timestamp,source_wallet,target_wallet,amount_btc,tx_hash,status\n"
            "2026-07-20 18:00:00,1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa,3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy,4.5,9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f0e,CONFIRMED\n"
            "2026-07-20 20:30:15,3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy,bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq,8.0,1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b,CONFIRMED\n"
        ).encode("utf-8")

        debrief = (
            "--- LEAD FORENSIC ANALYST AUDIO DEBRIEF ---\n"
            "Examiner: Senior Analyst K. Nair | Cyber Forensic Laboratory\n\n"
            "[00:00:05] ANALYST: We successfully bypassed the BitLocker encryption on the seized Western Digital SSD.\n"
            "[00:00:20] ANALYST: In the carved unallocated space, we identified communication matching suspect +919876543210.\n"
            "[00:00:35] ANALYST: Crucially, the Telegram SQLite database named @phantom_operator and referenced Alex Mercer.\n"
            "[00:00:50] ANALYST: Cryptographic transactions trace back to wallet 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa.\n"
        ).encode("utf-8")

        return [
            ("EV-01_autopsy_drive_recovery_log.txt", autopsy, "document", "text/plain", "Autopsy forensic extraction log of BitLocker encrypted NVMe drive"),
            ("EV-02_telegram_sqlite_chat_dump.txt", tg_chat, "chat_export", "text/plain", "Decrypted Telegram chat logs showing Bitcoin wallet addresses"),
            ("EV-03_safehouse_seizure_photo.jpg", photo, "image", "image/jpeg", "Forensic camera image of seized drive hardware in safehouse"),
            ("EV-04_crypto_transaction_ledger.csv", ledger, "call_log", "text/csv", "Extracted cryptocurrency transaction ledger with transaction hashes"),
            ("EV-05_analyst_debrief_audio.txt", debrief, "audio", "audio/wav", "Forensic audio debrief transcript explaining decryption methodology"),
        ]

    # 3. CS-2026-0004 & CS-2026-0005: Operation Shadow Phantom
    elif "shadow phantom" in title.lower() or "0004" in num or "0005" in num:
        cctv = create_forensic_image(
            title="SHADOW PHANTOM // SURVEILLANCE DROP POINT",
            subtitle="Dead Drop Locker 18 Identification",
            location_str="Central Railway Station, New Delhi",
            camera_make="Canon",
            camera_model="EOS R5 (Surveillance Body)",
            date_str="2026:08:05 19:45:10",
            lat=28.6448,
            lon=77.2167,
        )
        darknet_chat = (
            "--- DARKNET TOR MARKET CHAT INTERCEPT ---\n"
            "Operation Shadow Phantom // Intercepted PGP Chat\n\n"
            "[2026-08-05 18:20:00] User: ShadowViper | PGP Key ID: 0x4B29A01F\n"
            "Message: Package 4 has been dropped at Central Railway Station locker 18.\n"
            "Coordinate with courier +919811002233 for immediate pickup.\n"
            "Ensure burner phone IMEI 864920048192049 is turned off immediately after retrieval.\n"
            "Funds of 3.2 BTC sent to wallet 3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy.\n"
            "Direct all escrow disputes to shadow.phantom.admin@onionmail.org.\n"
        ).encode("utf-8")

        cdr = (
            "timestamp,caller_number,dialed_number,duration_sec,cell_tower,device_imei\n"
            "2026-08-05 18:15:00,+919811002233,+919876543210,120,New Delhi Railway Stn,864920048192049\n"
            "2026-08-05 18:45:30,+919811002233,+919123456789,90,Connaught Place,864920048192049\n"
            "2026-08-05 19:10:00,+919811002233,+919811002233,35,Pahar Ganj Tower,864920048192049\n"
        ).encode("utf-8")

        ledger = (
            "SHADOW PHANTOM SYNDICATE LEDGER (SEIZED SPREADSHEET)\n"
            "Operator Alias: ShadowViper\n"
            "Contact: shadow.phantom.admin@onionmail.org | Phone: +919811002233\n"
            "Drop 1: Kochi Port Container Yard | Courier: Alex Mercer\n"
            "Drop 2: New Delhi Station Locker 18 | Courier: John Mathew\n"
            "Primary Escrow Bitcoin Wallet: 3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy\n"
        ).encode("utf-8")

        wiretap = (
            "--- FEDERAL WIRETAP RECORDING TRANSCRIPT ---\n"
            "Target: +919811002233 (Shadow Syndicate Dispatch)\n"
            "Timestamp: 2026-08-05 19:30:00\n\n"
            "[00:00:10] CALLER 1: Did the locker courier pickup the package at New Delhi?\n"
            "[00:00:22] CALLER 2: Yes, ShadowViper confirmed the locker PIN was verified.\n"
            "[00:00:38] CALLER 1: Good. Tell John Mathew to transfer the escrow to +919876543210.\n"
            "[00:00:52] CALLER 2: Moving to safehouse now. Vehicle license plate KL-07-CD-4921.\n"
        ).encode("utf-8")

        return [
            ("EV-01_darknet_market_chat.txt", darknet_chat, "chat_export", "text/plain", "Encrypted darknet marketplace messaging detailing dead drop locker coordinates"),
            ("EV-02_dead_drop_surveillance.jpg", cctv, "image", "image/jpeg", "Surveillance photo of locker drop location with forensic EXIF and GPS"),
            ("EV-03_courier_telecom_cdr.csv", cdr, "call_log", "text/csv", "Call Detail Record tracking burner phone +919811002233 near railway station"),
            ("EV-04_syndicate_ledger_notes.txt", ledger, "document", "text/plain", "Seized operational ledger detailing couriers, drop points, and Bitcoin addresses"),
            ("EV-05_wiretap_intercept_audio.txt", wiretap, "audio", "audio/wav", "Recorded wiretap telephone intercept between syndicate members"),
        ]

    # 4. CS-2026-0006 through CS-2026-0014: Operation Cyber Fortress
    else:
        photo = create_forensic_image(
            title="OPERATION CYBER FORTRESS // COMPROMISED INFRASTRUCTURE",
            subtitle=f"Incident Analysis {num}",
            location_str="Critical Power Grid Substation 09, Bangalore",
            camera_make="Axis Communications",
            camera_model="Q1659 20MP Forensic Sensor",
            date_str="2026:08:12 04:15:33",
            lat=12.9716,
            lon=77.5946,
        )
        ransom_note = (
            "=========================================================================\n"
            "            CYBER FORTRESS RANSOMWARE EXTORTION NOTICE\n"
            "=========================================================================\n"
            "ATTENTION: All critical infrastructure servers and databases are ENCRYPTED.\n"
            "Impacted Domain: CYBERSHIELD.GOV.IN / SCADA Control Network\n\n"
            "To restore system operations and prevent publication of 850GB stolen data:\n"
            "1. You must transfer 8.5 Bitcoin to official address: bc1qa5wkgaew2dkv56kfvj49j0av5nqvrlph22ap4be\n"
            "2. Access your private negotiation portal on Tor: http://fortress7x9qwertyuioasdfghjklzxcvbnm.onion\n"
            "3. Emergency verification contact: incident.response@cyber-shield-syndicate.ru\n"
            "4. Operational Telegram dispatch handle: @fortress_ransom_ops (Phone: +79161234567)\n\n"
            "Deadline: August 15, 2026 at 12:00 UTC. If unpaid, all keys will be permanently destroyed.\n"
        ).encode("utf-8")

        pcap_logs = (
            "timestamp,source_ip,destination_ip,protocol,port,alert_signature\n"
            "2026-08-12 03:45:10,194.26.29.112,10.0.100.5,TCP,445,ET EXPLOIT PsExec Lateral Movement Remote Admin\n"
            "2026-08-12 03:52:18,10.0.100.5,10.0.100.12,TCP,88,ET ATTACK Kerberoasting Ticket Granting Service Request\n"
            "2026-08-12 04:02:45,10.0.100.12,198.51.100.42,TCP,443,ET C2 Cobalt Strike Beacon Traffic Observed\n"
            "2026-08-12 04:12:00,10.0.100.12,52.216.144.98,TCP,443,ET DATA Rclone Exfiltration Cloud Upload 850GB\n"
        ).encode("utf-8")

        threat_dossier = (
            "CYBER FORTRESS INCIDENT ATTRIBUTION DOSSIER\n"
            "Threat Actor Group: APT-88 'Cobalt Shadow'\n"
            "Command Center: 198.51.100.42 (Bulletproof Hosting Moldova)\n"
            "Lead Actor Identity: Dmitry Orlov (Alias: @fortress_ransom_ops)\n"
            "Associated Phone: +79161234567\n"
            "Associated Email: incident.response@cyber-shield-syndicate.ru\n"
            "Ransom Payment Address: bc1qa5wkgaew2dkv56kfvj49j0av5nqvrlph22ap4be\n"
            "Target Coordinates: Bangalore Electrical Grid Substation (12.9716 N, 77.5946 E)\n"
        ).encode("utf-8")

        debrief = (
            "--- INCIDENT RESPONSE COMMAND RECORDED AUDIO TRANSCRIPT ---\n"
            "Incident Commander: Col. S. Varma | National Cyber Defense Centre\n\n"
            "[00:00:05] COMMANDER: Cyber Fortress ransomware attack initiated against regional electrical grid.\n"
            "[00:00:22] COMMANDER: Attackers entered via compromised VPN from source IP 194.26.29.112.\n"
            "[00:00:40] COMMANDER: Extortion note demands 8.5 BTC to wallet bc1qa5wkgaew2dkv56kfvj49j0av5nqvrlph22ap4be.\n"
            "[00:00:58] COMMANDER: Cobalt Strike beacon communicating with C2 server 198.51.100.42.\n"
            "[00:01:15] COMMANDER: Isolate domain controller 10.0.100.12 immediately and preserve RAM dumps.\n"
        ).encode("utf-8")

        return [
            ("EV-01_cyber_fortress_ransom_note.txt", ransom_note, "document", "text/plain", "Ransomware extortion demand note deposited across compromised servers"),
            ("EV-02_scada_substation_cctv.jpg", photo, "image", "image/jpeg", "Perimeter security camera frame of power grid substation with GPS EXIF"),
            ("EV-03_firewall_intrusion_pcap_logs.csv", pcap_logs, "call_log", "text/csv", "Network intrusion detection log showing lateral movement and C2 beaconing"),
            ("EV-04_threat_actor_attribution_dossier.txt", threat_dossier, "document", "text/plain", "Intelligence dossier detailing APT-88 threat group and Bitcoin addresses"),
            ("EV-05_incident_commander_debrief.txt", debrief, "audio", "audio/wav", "Recorded audio debrief transcript from national cyber incident command"),
        ]


def seed_all_cases_evidence():
    """Iterate through all cases in the database and ensure complete synthetic evidence exists."""
    storage = get_storage()
    db = next(get_db())

    try:
        actor = db.query(User).filter(User.role == UserRole.investigator).first() or db.query(User).first()
        if not actor:
            print("[ERROR] No user found in database.")
            return

        cases = db.query(Case).order_by(Case.case_number.asc()).all()
        print(f"\n==================================================")
        print(f"FOUND {len(cases)} TOTAL CASES IN DATABASE")
        print(f"==================================================\n")

        pipeline = EvidencePipeline(db)

        for case in cases:
            existing_count = len(case.evidence_items)
            print(f"> Processing Case {case.case_number}: '{case.title}' (Existing Evidence: {existing_count})")

            # If case already has 4 or more evidence files (like CS-2026-0003), ensure case pipeline is refreshed
            if existing_count >= 4:
                print(f"  [INFO] Case already has {existing_count} evidence items. Refreshing pipeline...")
                pipe_res = pipeline.run_case_pipeline(case.id, actor_id=actor.id)
                print(f"  [OK] Pipeline refreshed: {pipe_res.get('correlations_found')} correlations, {pipe_res.get('leads_generated')} leads, Risk: {pipe_res.get('risk_score')}/100")
                continue

            # Generate synthetic evidence specs
            specs = get_case_evidence_specs(case)
            case_id_str = str(case.id)

            created_ev_list = []
            for orig_name, file_bytes, ftype, mtype, desc in specs:
                # Check if evidence with this original name already exists for this case
                existing_ev = (
                    db.query(Evidence)
                    .filter(Evidence.case_id == case.id, Evidence.original_name == orig_name)
                    .first()
                )
                if existing_ev:
                    created_ev_list.append(existing_ev)
                    continue

                # Save physical file to storage repo
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
                    tags=["synthetic_evidence", case.case_number.lower(), ftype],
                    uploaded_by_id=actor.id,
                    is_duplicate=False,
                )
                db.add(ev)
                db.flush()

                # Process single evidence through multimodal pipeline
                pipeline.process_single_evidence(ev.id)
                created_ev_list.append(ev)
                print(f"    + Created & Processed: {orig_name} ({ftype}, {len(file_bytes)} bytes)")

            db.commit()

            # Run full Case AI Intelligence Pipeline (Correlations, Timeline, Risk, Leads)
            print(f"  --> Running Case Intelligence Pipeline for {case.case_number}...")
            pipe_res = pipeline.run_case_pipeline(case.id, actor_id=actor.id)
            print(f"  [OK] Done! Correlations: {pipe_res.get('correlations_found')}, Timeline Events: {pipe_res.get('timeline_events_generated')}, Risk Score: {pipe_res.get('risk_score')}/100 ({pipe_res.get('risk_level')}), Leads: {pipe_res.get('leads_generated')}\n")

        print("==================================================")
        print("ALL CASES NOW HAVE COMPLETE SYNTHETIC EVIDENCE!")
        print("==================================================")

    finally:
        db.close()


if __name__ == "__main__":
    seed_all_cases_evidence()
