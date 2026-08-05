"""Notification helper."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.audit import Notification
from app.models.enums import NotificationType


def notify(
    db: Session,
    *,
    user_id: UUID,
    notification_type: NotificationType,
    title: str,
    message: str,
    link: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> Notification:
    n = Notification(
        user_id=user_id,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link,
        metadata_json=metadata,
    )
    db.add(n)
    return n
