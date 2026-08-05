"""RBAC helpers — departments, user provisioning, role-scoped stats."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role
from app.core.security import hash_password
from app.db.session import get_db
from app.models.case import Case
from app.models.department import Department
from app.models.enums import CaseStatus
from app.models.evidence import Evidence
from app.models.user import User, UserRole
from app.repositories.common import UserRepository
from app.schemas.domain import PageOut
from app.schemas.user import UserResponse
from app.utils.pagination import paginate

router = APIRouter(tags=["rbac"])


class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str | None = Field(default=None, max_length=64)
    description: str | None = None


class DepartmentOut(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    name: str
    code: str | None
    description: str | None
    is_active: bool


class ProvisionUser(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole
    department: str | None = None


class RoleStats(BaseModel):
    total_major_admins: int = 0
    total_admins: int = 0
    total_superior_officers: int = 0
    total_investigators: int = 0
    total_cases: int = 0
    active_cases: int = 0
    closed_cases: int = 0
    evidence_uploaded: int = 0
    departments: int = 0
    storage_bytes: int = 0


def _count_role(db: Session, role: UserRole) -> int:
    return (
        db.scalar(select(func.count()).select_from(User).where(User.role == role, User.is_active.is_(True)))
        or 0
    )


@router.get("/rbac/stats", response_model=RoleStats)
def rbac_stats(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> RoleStats:
    active = (
        db.scalar(
            select(func.count()).select_from(Case).where(
                Case.status.notin_([CaseStatus.completed, CaseStatus.archived])
            )
        )
        or 0
    )
    closed = (
        db.scalar(
            select(func.count()).select_from(Case).where(
                Case.status.in_([CaseStatus.completed, CaseStatus.archived])
            )
        )
        or 0
    )
    storage = db.scalar(select(func.coalesce(func.sum(Evidence.file_size), 0))) or 0
    return RoleStats(
        total_major_admins=_count_role(db, UserRole.major_admin),
        total_admins=_count_role(db, UserRole.admin),
        total_superior_officers=_count_role(db, UserRole.superior_officer),
        total_investigators=_count_role(db, UserRole.investigator),
        total_cases=db.scalar(select(func.count()).select_from(Case)) or 0,
        active_cases=active,
        closed_cases=closed,
        evidence_uploaded=db.scalar(select(func.count()).select_from(Evidence)) or 0,
        departments=db.scalar(select(func.count()).select_from(Department)) or 0,
        storage_bytes=int(storage),
    )


@router.get("/departments", response_model=list[DepartmentOut])
def list_departments(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    rows = list(db.scalars(select(Department).order_by(Department.name)).all())
    return [DepartmentOut.model_validate(r) for r in rows]


@router.post("/departments", response_model=DepartmentOut, status_code=201)
def create_department(
    payload: DepartmentCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_role(["major_admin"]))],
):
    existing = db.scalar(select(Department).where(Department.name == payload.name.strip()))
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Department already exists")
    row = Department(
        name=payload.name.strip(),
        code=payload.code.strip() if payload.code else None,
        description=payload.description,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return DepartmentOut.model_validate(row)


@router.delete("/departments/{department_id}")
def delete_department(
    department_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_role(["major_admin"]))],
):
    row = db.get(Department, department_id)
    if not row:
        raise HTTPException(404, detail="Department not found")
    db.delete(row)
    db.commit()
    return {"success": True}


@router.post("/rbac/users", response_model=UserResponse, status_code=201)
def provision_user(
    payload: ProvisionUser,
    db: Annotated[Session, Depends(get_db)],
    actor: Annotated[User, Depends(get_current_user)],
):
    """Role-gated user creation."""
    allowed: set[UserRole] = set()
    if actor.role == UserRole.major_admin:
        allowed = {UserRole.admin, UserRole.superior_officer, UserRole.investigator, UserRole.major_admin}
    elif actor.role == UserRole.admin:
        allowed = {UserRole.superior_officer, UserRole.investigator}
    elif actor.role == UserRole.superior_officer:
        allowed = {UserRole.investigator}
    else:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    if payload.role not in allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=f"Cannot create role {payload.role.value}")

    if db.scalar(select(User).where(User.email == payload.email.lower())):
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        full_name=payload.full_name.strip(),
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        role=payload.role,
        department=payload.department,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


@router.get("/rbac/users", response_model=PageOut[UserResponse])
def list_users_filtered(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    role: UserRole | None = None,
    q: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
):
    items, total = UserRepository(db).list(q=q, offset=(page - 1) * page_size, limit=page_size)
    if role:
        items = [u for u in items if u.role == role]
        # recount for filtered page (simple approach)
        all_users, _ = UserRepository(db).list(q=q, offset=0, limit=500)
        filtered = [u for u in all_users if u.role == role]
        return paginate(len(filtered), page, page_size, [UserResponse.model_validate(u) for u in filtered[(page - 1) * page_size : page * page_size]])
    return paginate(total, page, page_size, [UserResponse.model_validate(u) for u in items])
