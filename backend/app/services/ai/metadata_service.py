"""Forensic and technical metadata extraction for all supported evidence types."""

from __future__ import annotations

import datetime
import io
from pathlib import Path
from typing import Any

from PIL import ExifTags, Image

try:
    import pypdf
except ImportError:  # pragma: no cover
    pypdf = None  # type: ignore


class MetadataService:
    @staticmethod
    def extract_image_exif(data: bytes) -> dict[str, Any]:
        """Extract camera, device, lens, timestamp, and GPS metadata from image bytes."""
        exif_info: dict[str, Any] = {}
        try:
            img = Image.open(io.BytesIO(data))
            exif_info["width"] = img.width
            exif_info["height"] = img.height
            exif_info["format"] = img.format or "Unknown"

            raw_exif = img._getexif()
            if raw_exif:
                for tag_id, value in raw_exif.items():
                    tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                    if tag_name in (
                        "Make",
                        "Model",
                        "Software",
                        "DateTime",
                        "DateTimeOriginal",
                        "DateTimeDigitized",
                        "LensModel",
                        "ExposureTime",
                        "FNumber",
                        "ISOSpeedRatings",
                        "Artist",
                        "Copyright",
                    ):
                        exif_info[str(tag_name)] = str(value)
                    elif tag_name == "GPSInfo":
                        gps_dict: dict[str, Any] = {}
                        for k, v in value.items():
                            gps_tag = ExifTags.GPSTAGS.get(k, str(k))
                            gps_dict[str(gps_tag)] = str(v)
                        exif_info["GPSInfo"] = gps_dict

                        # Attempt to parse decimal coordinates if available
                        try:
                            lat_ref = gps_dict.get("GPSLatitudeRef")
                            lat = value.get(2)
                            lon_ref = gps_dict.get("GPSLongitudeRef")
                            lon = value.get(4)
                            if lat and lon:
                                def _to_deg(coord: Any) -> float:
                                    d, m, s = float(coord[0]), float(coord[1]), float(coord[2])
                                    return d + (m / 60.0) + (s / 3600.0)
                                dec_lat = _to_deg(lat)
                                if lat_ref == "S":
                                    dec_lat = -dec_lat
                                dec_lon = _to_deg(lon)
                                if lon_ref == "W":
                                    dec_lon = -dec_lon
                                exif_info["gps_coordinates"] = {
                                    "latitude": round(dec_lat, 6),
                                    "longitude": round(dec_lon, 6),
                                    "display": f"{round(dec_lat, 5)}, {round(dec_lon, 5)}",
                                }
                        except Exception:
                            pass
        except Exception:
            pass
        return exif_info

    @staticmethod
    def extract_pdf_metadata(data: bytes) -> dict[str, Any]:
        """Extract title, author, producer, creation date, and page count from PDF."""
        doc_info: dict[str, Any] = {}
        if pypdf is None:
            return doc_info
        try:
            reader = pypdf.PdfReader(io.BytesIO(data))
            doc_info["page_count"] = len(reader.pages)
            meta = reader.metadata
            if meta:
                if meta.title:
                    doc_info["title"] = str(meta.title)
                if meta.author:
                    doc_info["author"] = str(meta.author)
                if meta.creator:
                    doc_info["creator"] = str(meta.creator)
                if meta.producer:
                    doc_info["producer"] = str(meta.producer)
                if meta.creation_date:
                    doc_info["creation_date"] = str(meta.creation_date)
                if meta.modification_date:
                    doc_info["modification_date"] = str(meta.modification_date)
        except Exception:
            pass
        return doc_info

    @classmethod
    def extract_all_metadata(
        cls,
        data: bytes,
        filename: str,
        file_type: str,
        mime_type: str | None,
    ) -> dict[str, Any]:
        """
        Extract complete technical metadata with standardized fields.
        Uses real values when available, and standard 'Not Available' / 'Unknown' placeholders.
        """
        ext = Path(filename).suffix.lower()
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        meta: dict[str, Any] = {
            "filename": filename,
            "extension": ext or "Unknown",
            "mime_type": mime_type or "Unknown",
            "file_size_bytes": len(data),
            "file_size_formatted": f"{(len(data) / 1024):.1f} KB" if len(data) < 1024 * 1024 else f"{(len(data) / (1024 * 1024)):.2f} MB",
            "analyzed_at": now_iso,
            "device_info": "Not Available",
            "gps_coordinates": "Not Available",
            "camera_model": "Not Available",
            "author": "Not Available",
            "embedded_timestamps": [],
        }

        if file_type == "image":
            exif = cls.extract_image_exif(data)
            if exif:
                meta["exif"] = exif
                if "Make" in exif or "Model" in exif:
                    meta["camera_model"] = f"{exif.get('Make', '')} {exif.get('Model', '')}".strip()
                    meta["device_info"] = meta["camera_model"]
                if "DateTimeOriginal" in exif:
                    meta["creation_date"] = exif["DateTimeOriginal"]
                    meta["embedded_timestamps"].append(exif["DateTimeOriginal"])
                if "gps_coordinates" in exif:
                    meta["gps_coordinates"] = exif["gps_coordinates"]["display"]
                    meta["gps_detail"] = exif["gps_coordinates"]

        elif ext == ".pdf" or (mime_type and mime_type.lower() == "application/pdf"):
            pdf_meta = cls.extract_pdf_metadata(data)
            if pdf_meta:
                meta["document_metadata"] = pdf_meta
                if "author" in pdf_meta:
                    meta["author"] = pdf_meta["author"]
                if "creation_date" in pdf_meta:
                    meta["creation_date"] = pdf_meta["creation_date"]
                    meta["embedded_timestamps"].append(pdf_meta["creation_date"])
                if "page_count" in pdf_meta:
                    meta["page_count"] = pdf_meta["page_count"]

        return meta
