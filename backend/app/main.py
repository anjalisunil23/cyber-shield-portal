"""
Cyber Shield API entrypoint.

Interactive OpenAPI docs are available at /docs (Swagger UI) and /redoc.
"""

import sys
from pathlib import Path

_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.routes.auth import router as auth_router
from app.api.routes.admin import router as admin_router
from app.api.routes.cases import router as cases_router
from app.api.routes.evidence import router as evidence_router
from app.api.routes.modules import router as modules_router
from app.api.routes.platform import router as platform_router
from app.api.routes.rbac import router as rbac_router
from app.api.routes.chat import router as chat_router
from app.api.routes.ai import router as ai_router
from app.api.routes.repository import router as repository_router
from app.core.config import get_settings
from app.services.storage import ensure_upload_tree

settings = get_settings()
ensure_upload_tree()

app = FastAPI(
    title="CyberShield API",
    description="AI-powered investigation support platform — Making Evidence to Intelligence",
    version="2.0.0",
)

raw_origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
if "https://cyber-shield-portal.vercel.app" not in raw_origins:
    raw_origins.append("https://cyber-shield-portal.vercel.app")

allow_origins = ["*"] if "*" in raw_origins else raw_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_origin_regex=r"https://.*\.vercel\.app|http://localhost:.*|http://127\.0\.0\.1:.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


def _error_body(message: str) -> dict:
    return {"success": False, "message": message}


def _cors_headers(request: Request) -> dict:
    origin = request.headers.get("origin", "*")
    return {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Credentials": "true",
    }


@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        headers = _cors_headers(request)
        return JSONResponse(
            status_code=500,
            content=_error_body(f"Server error: {str(exc)}"),
            headers=headers,
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail
    if isinstance(detail, dict) and "message" in detail:
        body = {"success": False, "message": str(detail["message"])}
    elif isinstance(detail, str):
        body = _error_body(detail)
    else:
        body = _error_body("Request failed")
    headers = {**_cors_headers(request), **(exc.headers or {})}
    return JSONResponse(status_code=exc.status_code, content=body, headers=headers)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    errors = exc.errors()
    if errors:
        first = errors[0]
        loc = " -> ".join(str(p) for p in first.get("loc", []) if p != "body")
        msg = first.get("msg", "Validation error")
        message = f"{loc}: {msg}" if loc else msg
    else:
        message = "Validation error"
    return JSONResponse(status_code=422, content=_error_body(message), headers=_cors_headers(request))


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content=_error_body(f"Database error: {str(exc)}"),
        headers=_cors_headers(request),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=_error_body(f"Server error: {str(exc)}"),
        headers=_cors_headers(request),
    )


app.include_router(auth_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(cases_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(evidence_router, prefix="/api")
app.include_router(modules_router, prefix="/api")
app.include_router(platform_router, prefix="/api")
app.include_router(rbac_router, prefix="/api")
app.include_router(ai_router, prefix="/api")
app.include_router(repository_router, prefix="/api")


@app.get("/")
def root() -> dict:
    return {
        "success": True,
        "message": "CyberShield API",
        "docs": "/docs",
        "health": "/api/health",
        "phase": 2,
    }


@app.get("/api/health")
def health() -> dict:
    return {"success": True, "message": "ok"}


@app.get("/api/debug-env")
def debug_env() -> dict:
    from app.db.session import get_engine
    from sqlalchemy import text
    settings = get_settings()
    db_ok = False
    db_err = ""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            res = conn.execute(text("SELECT 1")).scalar()
            db_ok = bool(res == 1)
    except Exception as e:
        db_err = f"{type(e).__name__}: {str(e)}"

    return {
        "success": True,
        "database_url_set": bool(settings.database_url),
        "database_url_prefix": settings.database_url[:30] if settings.database_url else "",
        "database_connected": db_ok,
        "database_error": db_err,
        "jwt_secret_len": len(settings.jwt_secret),
    }
