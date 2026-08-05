"""Admin-module Pydantic schemas."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.models.enums import CasePriority, CaseStatus, ReportFormat
from app.models.user import UserRole
from app.schemas.domain import ActivityOut, CaseOut, EvidenceOut, NotificationOut, UserBrief


class AdminUserCreate(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=32)
    badge_number: str | None = Field(default=None, max_length=64)
    department_id: UUID | None = None
    department: str | None = Field(default=None, max_length=255)
    role: UserRole
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)
    is_active: bool = True

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        if len(value) < 8 or not re.search(r"\d", value):
            raise ValueError("Password must be at least 8 characters and contain at least one digit")
        return value

    @field_validator("role")
    @classmethod
    def admin_creatable_roles(cls, value: UserRole) -> UserRole:
        if value in {UserRole.major_admin, UserRole.admin}:
            raise ValueError("Admins can only create Superior Officers or Investigators")
        return value

    @model_validator(mode="after")
    def passwords_match(self) -> "AdminUserCreate":
        if self.password != self.confirm_password:
            raise ValueError("password and confirm_password must match")
        return self


class AdminUserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=32)
    badge_number: str | None = Field(default=None, max_length=64)
    department: str | None = Field(default=None, max_length=255)
    role: UserRole | None = None
    is_active: bool | None = None


class AdminPasswordReset(BaseModel):
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        if len(value) < 8 or not re.search(r"\d", value):
            raise ValueError("Password must be at least 8 characters and contain at least one digit")
        return value

    @model_validator(mode="after")
    def passwords_match(self) -> "AdminPasswordReset":
        if self.new_password != self.confirm_password:
            raise ValueError("new_password and confirm_password must match")
        return self


class AdminUserOut(BaseModel):
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


class AdminCaseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    priority: CasePriority = CasePriority.medium
    status: CaseStatus = CaseStatus.open
    notes: str | None = None
    superior_officer_id: UUID | None = None
    investigator_ids: list[UUID] = Field(default_factory=list)


class AdminCaseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = None
    priority: CasePriority | None = None
    status: CaseStatus | None = None
    notes: str | None = None
    superior_officer_id: UUID | None = None
    investigator_ids: list[UUID] | None = None


class AdminCaseAssign(BaseModel):
    superior_officer_id: UUID | None = None
    investigator_ids: list[UUID] = Field(default_factory=list)


class InvestigatorAssignmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    assigned_at: datetime
    user: UserBrief | None = None


class AdminCaseOut(CaseOut):
    department_id: UUID | None = None
    evidence_count: int = 0
    notes_count: int = 0
    timeline_count: int = 0
    superior_officer: UserBrief | None = None
    investigators: list[UserBrief] = Field(default_factory=list)
    investigator_assignments: list[InvestigatorAssignmentOut] = Field(default_factory=list)


class AdminDashboardStats(BaseModel):
    superior_officers: int
    investigators: int
    total_cases: int
    open_cases: int
    closed_cases: int
    evidence_count: int
    monthly_cases: list[dict[str, Any]] = Field(default_factory=list)
    evidence_types: list[dict[str, Any]] = Field(default_factory=list)
    priority_distribution: list[dict[str, Any]] = Field(default_factory=list)
    recent_activity: list[ActivityOut] = Field(default_factory=list)
    recent_cases: list[AdminCaseOut] = Field(default_factory=list)
    notifications: list[NotificationOut] = Field(default_factory=list)
    storage_bytes: int = 0


class AdminReportRequest(BaseModel):
    report_type: str = Field(..., pattern="^(case|department|investigator|evidence)$")
    case_id: UUID | None = None
    investigator_id: UUID | None = None
    format: ReportFormat = ReportFormat.csv
    title: str | None = None


class AdminReportOut(BaseModel):
    id: UUID | None = None
    title: str
    report_type: str
    format: ReportFormat
    content: str
    created_at: datetime | None = None
    summary: dict[str, Any] = Field(default_factory=dict)


class StorageUsageOut(BaseModel):
    total_files: int
    total_bytes: int
    by_type: list[dict[str, Any]] = Field(default_factory=list)


class EvidenceAdminOut(EvidenceOut):
    case_number: str | None = None
