"""Synthetic Evidence Repository generator tests (no network downloads)."""

from __future__ import annotations

import sys
from types import SimpleNamespace

from app.services.repository.file_factory import WATERMARK, sha256_bytes
from app.services.repository.generator import build_dataset, detect_theme


def _case(**kwargs):
    defaults = {
        "case_number": "CS-2026-0001",
        "title": "Wire fraud investigation",
        "description": "Phishing invoice and mule account activity",
        "notes": "",
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_theme_detection():
    assert detect_theme(_case(title="Missing child — Safe Haven", description="")) == "missing_person"
    assert detect_theme(_case(title="Ransomware intrusion", description="malware login records")) == "cybercrime"
    assert detect_theme(_case()) == "fraud"


def test_connected_dataset_and_duplicate_hash():
    files = build_dataset(_case(case_number="CS-2026-0003", title="Missing child"), include_duplicate=True)
    names = [f.filename for f in files]
    assert "investigator_notes.txt" in names
    assert "investigator_notes_duplicate.txt" in names
    assert "chat_export.txt" in names
    assert "call_log.csv" in names
    assert "gps_history.csv" in names
    original = next(f for f in files if f.filename == "investigator_notes.txt")
    duplicate = next(f for f in files if f.filename == "investigator_notes_duplicate.txt")
    assert original.data == duplicate.data
    assert sha256_bytes(original.data) == sha256_bytes(duplicate.data)
    textish = [f for f in files if f.filename.endswith((".txt", ".json", ".csv", ".eml"))]
    assert textish
    marker = b"SYNTHETIC DEMONSTRATION DATA"
    assert all(marker in f.data for f in textish)


def test_file_magic_and_sizes():
    files = {f.filename: f for f in build_dataset(_case(title="Cyber intrusion malware", description="hacked login records"), include_duplicate=False)}
    pdf = files["witness_statement.pdf"].data
    assert pdf.startswith(b"%PDF")
    wav = files["investigator_audio_note.wav"].data
    assert wav.startswith(b"RIFF")
    png = files["ocr_investigator_note.png"].data
    assert png.startswith(b"\x89PNG")
    for f in files.values():
        assert len(f.data) < 1_000_000, f"{f.filename} too large: {len(f.data)}"
        assert f.data, f"{f.filename} empty"


def test_personas_are_fictional():
    files = build_dataset(_case(case_number="CS-TEST-9", title="General inquiry"))
    blob = b" ".join(f.data for f in files if f.filename.endswith((".txt", ".json", ".csv")))
    assert b"cybershield.test" in blob
    assert b"SYNTHETIC DEMONSTRATION DATA" in blob


if __name__ == "__main__":
    test_theme_detection()
    print("  [OK] theme detection")
    test_connected_dataset_and_duplicate_hash()
    print("  [OK] duplicate SHA-256 + correlated files")
    test_file_magic_and_sizes()
    print("  [OK] PDF/WAV/PNG magic and size limits")
    test_personas_are_fictional()
    print("  [OK] fictional .test identities + watermark")
    print("Evidence repository generator tests passed.")
    sys.exit(0)
