"""Database queries for the audit trail."""

import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import defer

from app.model.audit_log import AuditLog
from app.repository.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    model = AuditLog
    search_fields = (AuditLog.action, AuditLog.entity_type, AuditLog.request_id)
    sort_fields = ("id", "created_at", "action", "entity_type")
    list_options = (  # A page does not show these large columns, so do not load them
        defer(AuditLog.details),
        defer(AuditLog.user_agent),
        defer(AuditLog.ip_address),
    )

    def db_now(self) -> datetime.datetime:  # Database time, the same clock as created_at
        return self.db.scalar(select(func.now()))

    def count_events(self, user_id: int, action: str, since: datetime.datetime) -> int:
        stmt = select(func.count(AuditLog.id)).where(
            AuditLog.user_id == user_id, AuditLog.action == action, AuditLog.created_at >= since
        )
        return self.db.scalar(stmt) or 0

    def last_event_time(self, user_id: int, action: str) -> datetime.datetime | None:
        stmt = select(func.max(AuditLog.created_at)).where(
            AuditLog.user_id == user_id, AuditLog.action == action
        )
        return self.db.scalar(stmt)
