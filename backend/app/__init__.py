"""CyberShield Phase 1 — investigation platform (no AI).

Architecture
- Repository → Service → API route layers
- Local file storage (swap STORAGE_BACKEND later for S3/MinIO)
- Evidence AI columns reserved but unused

Run
  docker compose up -d
  alembic upgrade head
  uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload

Docs: http://127.0.0.1:8001/docs
"""
