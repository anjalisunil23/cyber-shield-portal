"""Storage abstraction — local filesystem now; MinIO/S3 later without changing callers."""

from __future__ import annotations

import hashlib
import shutil
import uuid
from abc import ABC, abstractmethod
from pathlib import Path

from app.core.config import get_settings


class StorageBackend(ABC):
    @abstractmethod
    def save(self, *, case_id: str, filename: str, data: bytes) -> tuple[str, str]:
        """Persist bytes. Returns (storage_path, sha256_hex)."""

    @abstractmethod
    def open_path(self, storage_path: str) -> Path:
        """Resolve a storage path to a local readable path (for streaming)."""

    @abstractmethod
    def delete(self, storage_path: str) -> None:
        ...


class LocalStorageBackend(StorageBackend):
    """Writes under UPLOAD_DIR/{case_id}/{uuid}_{safe_name}."""

    def __init__(self, root: str | Path | None = None) -> None:
        settings = get_settings()
        self.root = Path(root or settings.upload_dir)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, *, case_id: str, filename: str, data: bytes) -> tuple[str, str]:
        safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in filename)[:200]
        folder = self.root / case_id
        folder.mkdir(parents=True, exist_ok=True)
        stored_name = f"{uuid.uuid4().hex}_{safe}"
        path = folder / stored_name
        path.write_bytes(data)
        digest = hashlib.sha256(data).hexdigest()
        # Relative path for portability
        rel = str(path.relative_to(self.root)).replace("\\", "/")
        return rel, digest

    def open_path(self, storage_path: str) -> Path:
        path = (self.root / storage_path).resolve()
        if not str(path).startswith(str(self.root.resolve())):
            raise ValueError("Invalid storage path")
        return path

    def delete(self, storage_path: str) -> None:
        path = self.open_path(storage_path)
        if path.exists():
            path.unlink()


def get_storage() -> StorageBackend:
    settings = get_settings()
    backend = (settings.storage_backend or "local").lower()
    if backend == "local":
        return LocalStorageBackend()
    # Placeholders for Phase 2 / infra swap
    if backend in {"s3", "minio"}:
        raise NotImplementedError(
            f"STORAGE_BACKEND={backend} is reserved for Phase 2. Use local for now."
        )
    return LocalStorageBackend()


def ensure_upload_tree() -> None:
    LocalStorageBackend()
