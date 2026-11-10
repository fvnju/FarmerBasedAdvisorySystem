"""Schemas for the audit trail. The API can only read it."""

from datetime import datetime
from typing import Any

from app.schema.common import ListQuery, ReadSchema


class AuditLogRead(ReadSchema):
    id: int
    user_id: int | None
    action: str
    entity_type: str | None
    entity_id: int | None
    details: Any | None
    ip_address: str | None
    user_agent: str | None
    request_id: str | None
    created_at: datetime


class AuditLogListItem(ReadSchema):  # Page item without the details, so the page stays small
    id: int
    user_id: int | None
    action: str
    entity_type: str | None
    entity_id: int | None
    request_id: str | None
    created_at: datetime


class AuditLogQuery(ListQuery):
    user_id: int | None = None
    action: str | None = None
    entity_type: str | None = None
    entity_id: int | None = None
    request_id: str | None = None
