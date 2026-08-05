"""
FastAPI dependencies: current user resolution and role gates.
"""

from collections.abc import Callable
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import JWTError, decode_access_token
from app.db.session import get_db
from app.models.user import User, UserRole

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """
    Decode ``Authorization: Bearer <token>``, verify the JWT, and load the user.
    Raises 401 if the header is missing, the token is invalid/expired, or the user
    is missing / inactive.
    """
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"success": False, "message": "Could not validate credentials"},
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized

    try:
        payload = decode_access_token(credentials.credentials)
        subject = payload.get("sub")
        if not subject:
            raise unauthorized
        user_id = UUID(str(subject))
    except (JWTError, ValueError):
        raise unauthorized from None

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise unauthorized

    return user


def require_role(allowed_roles: list[str]) -> Callable[..., User]:
    """
    Dependency factory: raise 403 if ``current_user.role`` is not in ``allowed_roles``.

    Usage::

        @router.get("/admin-only")
        def admin_route(user: User = Depends(require_role(["admin"]))):
            ...
    """
    allowed_values = {
        r.value if isinstance(r, UserRole) else str(r) for r in allowed_roles
    }

    def _dependency(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role.value not in allowed_values:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"success": False, "message": "Insufficient permissions"},
            )
        return current_user

    return _dependency
