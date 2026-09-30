"""
Cyber Shield API — application settings.

Secrets (DATABASE_URL, JWT_SECRET) are loaded from environment / .env only.
Never hardcode credentials or log JWT secrets / passwords.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_ENV_FILE = _BACKEND_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE) if _ENV_FILE.exists() else None,
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
        default="https://cyber-shield-portal.vercel.app,http://localhost:8080,http://localhost:8081,http://localhost:5173",
        alias="CORS_ORIGINS",
    )
    # Local uploads — swap STORAGE_BACKEND to s3/minio in Phase 2 without changing callers
    storage_backend: str = Field(default="local", alias="STORAGE_BACKEND")
    upload_dir: str = Field(default=str(_BACKEND_ROOT / "uploads"), alias="UPLOAD_DIR")
    max_upload_bytes: int = Field(default=500 * 1024 * 1024, alias="MAX_UPLOAD_BYTES")  # 500MB
    password_reset_expires_minutes: int = Field(default=60, alias="PASSWORD_RESET_EXPIRES_MINUTES")
    # In development, forgot-password may echo the reset token when no email provider is configured
    expose_reset_token: bool = Field(default=True, alias="EXPOSE_RESET_TOKEN")

    # AI / intelligence — optional; the app stays usable without keys or local models
    ai_provider: str = Field(default="local", alias="AI_PROVIDER")
    ai_api_key: str = Field(default="", alias="AI_API_KEY")
    ai_model_name: str = Field(default="gpt-4o-mini", alias="MODEL_NAME")
    ocr_engine: str = Field(default="auto", alias="OCR_ENGINE")
    whisper_model: str = Field(default="base", alias="WHISPER_MODEL")
    risk_low_max: int = Field(default=25, alias="RISK_LOW_MAX")
    risk_medium_max: int = Field(default=50, alias="RISK_MEDIUM_MAX")
    risk_high_max: int = Field(default=75, alias="RISK_HIGH_MAX")
    evidence_repository_dir: str = Field(
        default=str(_BACKEND_ROOT / "evidence_repository"),
        alias="EVIDENCE_REPOSITORY_DIR",
    )

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        """Render PostgreSQL uses postgres:// which SQLAlchemy 2.0 requires as postgresql://"""
        if isinstance(v, str) and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    @field_validator("jwt_secret", mode="before")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        """Ensure JWT_SECRET is provided and not set to insecure default placeholders."""
        if not v or not isinstance(v, str) or not v.strip():
            raise ValueError("JWT_SECRET environment variable must be set and non-empty.")
        cleaned = v.strip()
        insecure_placeholders = {"change-me-in-production", "secret", "jwt_secret", "password", "123456"}
        if cleaned.lower() in insecure_placeholders:
            raise ValueError(
                f"Insecure JWT_SECRET value '{cleaned}'. Set a strong random secret via environment variables."
            )
        if len(cleaned) < 16:
            raise ValueError("JWT_SECRET must be at least 16 characters long.")
        return cleaned

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
