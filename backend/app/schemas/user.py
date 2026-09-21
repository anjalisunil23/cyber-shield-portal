"""Pydantic request/response schemas for auth and users."""

import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.models.user import UserRole


class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)
    confirm_password: str = Field(..., min_length=8, max_length=64)
    role: UserRole
    department: str | None = Field(default=None, max_length=255)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        trimmed = value.strip()
        if len(trimmed) < 2 or len(trimmed) > 50 or not re.match(r"^[A-Za-z]+(?: [A-Za-z]+)*$", trimmed):
            raise ValueError("Please enter a valid full name.")
        return trimmed

    @field_validator("email")
    @classmethod
    def validate_gmail(cls, value: str) -> str:
        clean = str(value).strip().lower()
        if not re.match(r"^[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*@gmail\.com$", clean):
            raise ValueError("Please enter a valid Gmail address.")
        return clean

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        if (
            len(value) < 8
            or len(value) > 64
            or not re.search(r"[A-Z]", value)
            or not re.search(r"[a-z]", value)
            or not re.search(r"\d", value)
            or not re.search(r"[^A-Za-z0-9\s]", value)
            or re.search(r"\s", value)
        ):
            raise ValueError("Password does not meet all requirements.")
        return value

    @model_validator(mode="after")
    def passwords_match(self) -> "UserRegister":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        return self


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class UserResponse(BaseModel):
    """Sanitized user output — never includes password_hash."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    email: EmailStr
    role: UserRole
    department: str | None
    department_id: UUID | None = None
    phone: str | None = None
    badge_number: str | None = None
    profile_image_url: str | None = None
    is_active: bool
    created_at: datetime
    last_login: datetime | None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str | None = None
