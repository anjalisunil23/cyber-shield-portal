"""Department-scoped helpers for Admin RBAC."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status

from app.models.user import User, UserRole


def admin_department_id(actor: User) -> UUID | None:
    """Return department scope. None means unrestricted (major_admin only)."""
    if actor.role == UserRole.major_admin:
        return None
    if actor.role != UserRole.admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Admin role required")
    if not actor.department_id:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Admin account has no department assigned. Contact Major Admin.",
        )
    return actor.department_id


def assert_same_department(actor: User, target: User) -> None:
    scope = admin_department_id(actor)
    if scope is None:
        return
    if target.department_id != scope:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="User is outside your department")
    if target.role in {UserRole.major_admin, UserRole.admin}:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Cannot manage Admin accounts")


def assert_admin_creatable_role(role: UserRole) -> None:
    if role in {UserRole.major_admin, UserRole.admin}:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="Admins cannot create Admin or Major Admin accounts",
        )
