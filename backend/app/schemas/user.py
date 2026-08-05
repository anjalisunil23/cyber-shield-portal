"""Pydantic request/response schemas for auth and users."""

import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.models.user import UserRole


class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)
    role: UserRole
    department: str | None = Field(default=None, max_length=255)

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        # Minimum strength: 8+ characters and at least one digit
        if len(value) < 8 or not re.search(r"\d", value):
            raise ValueError("Password must be at least 8 characters and contain at least one digit")
        return value

    @model_validator(mode="after")
    def passwords_match(self) -> "UserRegister":
        if self.password != self.confirm_password:
            raise ValueError("password and confirm_password must match")
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
