"""Local synthetic file builders. No internet downloads. All files are watermarked."""

from __future__ import annotations

import hashlib
import io
import math
import struct
import subprocess
import tempfile
import textwrap
import wave
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

WATERMARK = "SYNTHETIC DEMONSTRATION DATA — NOT REAL FORENSIC EVIDENCE"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _font(size: int = 16) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def build_ocr_image(title: str, lines: list[str], *, width: int = 900, height: int = 640) -> bytes:
    img = Image.new("RGB", (width, height), color=(248, 250, 252))
    draw = ImageDraw.Draw(img)
    draw.rectangle([12, 12, width - 13, height - 13], outline=(37, 99, 235), width=3)
    draw.rectangle([12, 12, width - 13, 58], fill=(15, 23, 42))
    draw.text((24, 24), WATERMARK, fill=(248, 250, 252), font=_font(14))
    y = 76
    draw.text((28, y), title, fill=(15, 23, 42), font=_font(22))
    y += 36
    for line in lines:
        draw.text((28, y), line[:90], fill=(30, 41, 59), font=_font(16))
        y += 26
        if y > height - 40:
            break
    draw.text((28, height - 36), "Cyber Shield demo dataset · fictional identities only", fill=(100, 116, 139), font=_font(12))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def build_map_image(location: str, lat: str, lon: str, event: str) -> bytes:
    img = Image.new("RGB", (720, 480), color=(226, 232, 240))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 719, 40], fill=(15, 23, 42))
    draw.text((16, 12), WATERMARK, fill=(226, 232, 240), font=_font(13))
    for i in range(8):
        draw.line([(0, 80 + i * 48), (720, 80 + i * 48)], fill=(203, 213, 225), width=1)
        draw.line([(60 + i * 80, 40), (60 + i * 80, 480)], fill=(203, 213, 225), width=1)
    draw.ellipse([330, 210, 390, 270], outline=(220, 38, 38), width=4)
    draw.ellipse([352, 232, 368, 248], fill=(220, 38, 38))
    draw.rectangle([40, 360, 680, 460], fill=(255, 255, 255), outline=(37, 99, 235), width=2)
    draw.text((56, 372), f"SYNTHETIC MAP · {location}", fill=(15, 23, 42), font=_font(16))
    draw.text((56, 400), f"Coordinates: {lat}, {lon}", fill=(51, 65, 85), font=_font(14))
    draw.text((56, 426), event[:80], fill=(71, 85, 105), font=_font(14))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def build_pdf(title: str, paragraphs: list[str]) -> bytes:
    """Minimal one-page PDF with Helvetica text. No external PDF library required."""
    lines = [WATERMARK, "", title, ""]
    for para in paragraphs:
        lines.extend(textwrap.wrap(para, width=92) or [""])
        lines.append("")
    content_lines = []
    y = 760
    for line in lines[:42]:
        safe = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        content_lines.append(f"BT /F1 10 Tf 40 {y} Td ({safe}) Tj ET")
        y -= 16
    stream = "\n".join(content_lines).encode("latin-1", errors="replace")
    objects = []

    def obj(n: int, body: bytes) -> bytes:
        return f"{n} 0 obj\n".encode() + body + b"\nendobj\n"

    objects.append(obj(1, b"<< /Type /Catalog /Pages 2 0 R >>"))
    objects.append(obj(2, b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>"))
    objects.append(
        obj(
            3,
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        )
    )
    objects.append(obj(4, b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream"))
    objects.append(obj(5, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"))

    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for chunk in objects:
        offsets.append(len(out))
        out.extend(chunk)
    xref_pos = len(out)
    out.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    out.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        out.extend(f"{off:010d} 00000 n \n".encode())
    out.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode()
    )
    return bytes(out)


def build_docx(title: str, paragraphs: list[str]) -> bytes:
    ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    ET.register_namespace("w", ns)
    w = f"{{{ns}}}"
    document = ET.Element(f"{w}document")
    body = ET.SubElement(document, f"{w}body")

    def add_p(text: str, bold: bool = False) -> None:
        p = ET.SubElement(body, f"{w}p")
        r = ET.SubElement(p, f"{w}r")
        if bold:
            rpr = ET.SubElement(r, f"{w}rPr")
            ET.SubElement(rpr, f"{w}b")
        t = ET.SubElement(r, f"{w}t")
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        t.text = text

    add_p(WATERMARK, bold=True)
    add_p(title, bold=True)
    add_p("")
    for para in paragraphs:
        add_p(para)

    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""
    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("word/document.xml", ET.tostring(document, encoding="utf-8", xml_declaration=True))
    return buf.getvalue()


def build_wav(duration_sec: float = 6.0, freq: float = 440.0) -> bytes:
    """Valid 16-bit mono WAV tone. No speech claimed unless TTS is available."""
    rate = 16000
    n = int(rate * duration_sec)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        frames = bytearray()
        for i in range(n):
            sample = int(12000 * math.sin(2 * math.pi * freq * (i / rate)) * (0.4 + 0.6 * ((i % 4000) / 4000)))
            frames.extend(struct.pack("<h", max(-32767, min(32767, sample))))
        wf.writeframes(bytes(frames))
    return buf.getvalue()


def try_tts_wav(text: str) -> bytes | None:
    try:
        import pyttsx3  # type: ignore
    except ImportError:
        return None
    try:
        engine = pyttsx3.init()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            path = tmp.name
        engine.save_to_file(f"{WATERMARK}. {text}", path)
        engine.runAndWait()
        data = Path(path).read_bytes()
        Path(path).unlink(missing_ok=True)
        return data if data else None
    except Exception:
        return None


def build_video(frames_text: list[str], seconds: int = 6) -> tuple[bytes, str, str]:
    """
    Return (bytes, extension, mime). Prefers ffmpeg MP4; falls back to animated GIF.
    """
    frames: list[Image.Image] = []
    for idx, line in enumerate(frames_text[:8] or ["Synthetic briefing"]):
        img = Image.new("RGB", (480, 270), color=(15, 23, 42))
        draw = ImageDraw.Draw(img)
        draw.rectangle([8, 8, 471, 261], outline=(56, 189, 248), width=2)
        draw.text((20, 20), WATERMARK, fill=(148, 163, 184), font=_font(11))
        draw.text((20, 70), f"SYNTHETIC BRIEFING SLIDE {idx + 1}", fill=(226, 232, 240), font=_font(16))
        draw.text((20, 120), line[:48], fill=(125, 211, 252), font=_font(14))
        draw.text((20, 220), "Cyber Shield demonstration video", fill=(148, 163, 184), font=_font(12))
        frames.append(img)

    import shutil

    if shutil.which("ffmpeg") and frames:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            for i, frame in enumerate(frames):
                frame.save(tmp_path / f"f{i:03d}.png")
            out = tmp_path / "clip.mp4"
            cmd = [
                "ffmpeg",
                "-y",
                "-framerate",
                "1",
                "-i",
                str(tmp_path / "f%03d.png"),
                "-t",
                str(seconds),
                "-pix_fmt",
                "yuv420p",
                str(out),
            ]
            try:
                subprocess.run(cmd, check=True, capture_output=True, timeout=20)
                if out.exists() and out.stat().st_size > 0:
                    return out.read_bytes(), ".mp4", "video/mp4"
            except Exception:
                pass

    gif_buf = io.BytesIO()
    if frames:
        frames[0].save(
            gif_buf,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            duration=800,
            loop=0,
        )
    return gif_buf.getvalue(), ".gif", "image/gif"


def write_repo_file(root: Path, case_number: str, category: str, filename: str, data: bytes) -> Path:
    folder = root / case_number / category
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / filename
    path.write_bytes(data)
    return path


def relative_repo_path(root: Path, path: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")
