"""
Cyber Shield API — application settings.

Secrets (DATABASE_URL, JWT_SECRET) are loaded from environment / .env only.
Never hardcode credentials or log JWT secrets / passwords.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_ENV_FILE = _BACKEND_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    database_url: str = Field(..., alias="DATABASE_URL")
    jwt_secret: str = Field(..., alias="JWT_SECRET")
    jwt_expires_minutes: int = Field(default=60, alias="JWT_EXPIRES_MINUTES")
    jwt_refresh_expires_days: int = Field(default=14, alias="JWT_REFRESH_EXPIRES_DAYS")
    jwt_algorithm: str = "HS256"
    port: int = Field(default=8000, alias="PORT")
    cors_origins: str = Field(
        default="http://localhost:8080,http://localhost:8081",
        alias="CORS_ORIGINS",
    )
    # Local uploads — swap STORAGE_BACKEND to s3/minio in Phase 2 without changing callers
    storage_backend: str = Field(default="local", alias="STORAGE_BACKEND")
    upload_dir: str = Field(default=str(_BACKEND_ROOT / "uploads"), alias="UPLOAD_DIR")
    max_upload_bytes: int = Field(default=500 * 1024 * 1024, alias="MAX_UPLOAD_BYTES")  # 500MB
    password_reset_expires_minutes: int = Field(default=60, alias="PASSWORD_RESET_EXPIRES_MINUTES")
    # In development, forgot-password may echo the reset token when no email provider is configured
    expose_reset_token: bool = Field(default=True, alias="EXPOSE_RESET_TOKEN")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
