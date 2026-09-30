"""Database engine and session factory."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def get_engine() -> Engine:
    """Lazily create the engine so .env changes are picked up after restart."""
    global _engine, _SessionLocal
    if _engine is None:
        settings = get_settings()
        connect_args = {}
        if "render.com" in settings.database_url or "dpg-" in settings.database_url:
            connect_args["sslmode"] = "require"
        _engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            connect_args=connect_args,
        )
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    return _engine


def get_db() -> Generator[Session, None, None]:
    """Yield a request-scoped SQLAlchemy session and close it afterwards."""
    from fastapi import HTTPException
    from sqlalchemy import text
    try:
        get_engine()
        assert _SessionLocal is not None
        db = _SessionLocal()
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Database error ({type(exc).__name__}): {str(exc)}. Please check DATABASE_URL in Render Dashboard.",
        )
    try:
        yield db
    finally:
        db.close()
