# Cyber Shield Backend

Python / FastAPI authentication API for the Cyber Shield investigation platform.
Uses PostgreSQL (SQLAlchemy ORM) and Alembic migrations.

## Stack

- FastAPI + Uvicorn
- PostgreSQL + SQLAlchemy 2.x + Alembic
- passlib (bcrypt) password hashing
- python-jose JWT access tokens
- pydantic-settings for configuration

## Setup

### 1. Create a database

```sql
CREATE DATABASE cyber_shield;
```

### 2. Configure environment

```sh
cd backend
cp .env.example .env
# Edit DATABASE_URL and JWT_SECRET
```

Required variables:

| Variable              | Description                           |
| --------------------- | ------------------------------------- |
| `DATABASE_URL`        | PostgreSQL connection string          |
| `JWT_SECRET`          | Long random secret used to sign JWTs  |
| `JWT_EXPIRES_MINUTES` | Token lifetime (default `1440` = 24h) |
| `PORT`                | API listen port (default `8001`)      |
| `CORS_ORIGINS`        | Comma-separated frontend origins      |

### 3. Install dependencies

```sh
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 4. Run migrations

```sh
alembic upgrade head
```

### 5. Start the API

```sh
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Interactive docs: [http://localhost:8001/docs](http://localhost:8001/docs)

## Auth endpoints

| Method | Path                 | Description                                |
| ------ | -------------------- | ------------------------------------------ |
| `GET`  | `/api/health`        | Health check                               |
| `POST` | `/api/auth/register` | Create account → `201` + `UserResponse`    |
| `POST` | `/api/auth/login`    | Login → JWT (`access_token`, `token_type`) |

### Register body

```json
{
  "full_name": "Alex Rivera",
  "email": "alex@example.com",
  "password": "Secure1Pass",
  "confirm_password": "Secure1Pass",
  "role": "investigator",
  "department": "Cyber Unit"
}
```

Roles: `investigator`, `forensic_officer`, `supervisor`, `admin`

### Login body

```json
{
  "email": "alex@example.com",
  "password": "Secure1Pass"
}
```

## Security notes

- Passwords are hashed with bcrypt; plain text is never stored or logged
- JWT payload: `{ "sub": "<user_id>", "role": "<role>" }`
- Errors use a consistent shape: `{ "success": false, "message": "..." }`
- Use `get_current_user` / `require_role([...])` from `app.core.deps` to protect future routes
- CORS is restricted to `CORS_ORIGINS`
- Lead verify/reject/modify endpoints enforce case access
- Secrets stay in environment variables; they are never returned by `/api/ai/status`

## Intelligence services

Reusable processors live in `app/services/ai/` and are orchestrated by `EvidencePipeline`:

- `hash_service` — SHA-256 + duplicate lookup
- `metadata_service` — EXIF / PDF metadata (`Not Available` when absent)
- `text_service` / `ocr_service` / `transcription_service` — content extraction with fallbacks
- `entity_service` — regex + heuristic NER with normalization and context
- `correlation_service` / `timeline_service` / `risk_service` / `lead_service`
- `rag_service` / `summary_service` / `llm_service` — grounded search and summaries

Key routes (all under `/api`, all require auth + case access):

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/evidence/{id}/process` | Re-run single-file pipeline |
| `GET` | `/evidence/{id}/analysis` | Hash, metadata, OCR/STT, entities |
| `POST` | `/cases/{id}/pipeline` | Full case intelligence run |
| `GET` | `/cases/{id}/entities` | Aggregated normalized entities |
| `GET` | `/cases/{id}/correlations` | Cross-source matches |
| `GET` | `/cases/{id}/risk` | Explainable priority score |
| `GET` | `/cases/{id}/graph` | Relationship graph |
| `POST` | `/cases/{id}/search` | Grounded natural-language search |
| `POST` | `/cases/{id}/summarize` | Investigation summary |
| `GET` | `/cases/{id}/intelligence-export` | JSON export |
| `GET` | `/cases/{id}/audit-log` | Case activity |
| `POST` | `/leads/{id}/verify\|reject\|modify` | Human oversight |
| `GET` | `/ai/status` | Engine availability (no secrets) |
