"""Authentication routes: register, login, refresh, logout, me, password reset, profile."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_user
from app.core.security import (
    create_access_token,
    create_refresh_token_value,
    hash_password,
    hash_token,
    password_reset_expiry,
    refresh_token_expiry,
    verify_password,
)
from app.db.session import get_db
from app.models.audit import PasswordResetToken, RefreshToken
from app.models.enums import ActivityAction
from app.models.user import User
from app.schemas.domain import (
    ForgotPasswordRequest,
    PasswordChange,
    RefreshRequest,
    ResetPasswordRequest,
    TokenPair,
    UserUpdate,
)
from app.schemas.user import Token, UserLogin, UserRegister, UserResponse
from app.services.activity import log_activity

router = APIRouter(prefix="/auth", tags=["auth"])


def _issue_tokens(db: Session, user: User) -> TokenPair:
    access = create_access_token(subject=user.id, role=user.role.value)
    raw_refresh = create_refresh_token_value()
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_token(raw_refresh),
            expires_at=refresh_token_expiry(),
        )
    )
    db.commit()
    return TokenPair(
        access_token=access,
        refresh_token=raw_refresh,
        role=user.role.value,
        user_id=str(user.id),
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Annotated[Session, Depends(get_db)]) -> User:
    existing = db.scalar(select(User).where(User.email == payload.email.lower()))
    if existing is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        full_name=payload.full_name.strip(),
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        role=payload.role,
        department=payload.department.strip() if payload.department else None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenPair)
def login(
    payload: UserLogin,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> TokenPair:
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user.last_login = datetime.now(timezone.utc)
    log_activity(
        db,
        user_id=user.id,
        action=ActivityAction.login,
        description=f"Login {user.email}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(user)
    return _issue_tokens(db, user)


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, db: Annotated[Session, Depends(get_db)]) -> TokenPair:
    th = hash_token(payload.refresh_token)
    row = db.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == th,
            RefreshToken.revoked.is_(False),
        )
    )
    if row is None or row.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user = db.get(User, row.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    row.revoked = True
    db.add(row)
    return _issue_tokens(db, user)


@router.post("/logout")
def logout(
    payload: RefreshRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    th = hash_token(payload.refresh_token)
    row = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == th, RefreshToken.user_id == current_user.id))
    if row:
        row.revoked = True
        db.add(row)
    log_activity(
        db,
        user_id=current_user.id,
        action=ActivityAction.logout,
        description=f"Logout {current_user.email}",
    )
    db.commit()
    return {"success": True, "message": "Logged out"}


@router.get("/me", response_model=UserResponse)
def me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_me(
    payload: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(current_user, k, v)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/change-password")
def change_password(
    payload: PasswordChange,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    current_user.password_hash = hash_password(payload.new_password)
    db.add(current_user)
    db.commit()
    return {"success": True, "message": "Password updated"}


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Annotated[Session, Depends(get_db)]) -> dict:
    """Always returns success to avoid email enumeration. Token echoed when EXPOSE_RESET_TOKEN=true."""
    settings = get_settings()
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    response: dict = {
        "success": True,
        "message": "If that email exists, a reset token has been issued.",
    }
    if user and user.is_active:
        raw = create_refresh_token_value()
        db.add(
            PasswordResetToken(
                user_id=user.id,
                token_hash=hash_token(raw),
                expires_at=password_reset_expiry(),
            )
        )
        db.commit()
        if settings.expose_reset_token:
            response["reset_token"] = raw
    return response


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Annotated[Session, Depends(get_db)]) -> dict:
    th = hash_token(payload.token)
    row = db.scalar(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == th,
            PasswordResetToken.used.is_(False),
        )
    )
    if row is None or row.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")
    user = db.get(User, row.user_id)
    if not user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")
    user.password_hash = hash_password(payload.new_password)
    row.used = True
    db.add(user)
    db.add(row)
    db.commit()
    return {"success": True, "message": "Password has been reset"}
