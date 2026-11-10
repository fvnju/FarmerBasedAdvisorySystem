"""Controllers for audit logs."""

from app.controller.base import BaseController
from app.schema.audit_log import (
    AuditLogListItem,
    AuditLogQuery,
    AuditLogRead,
)
from app.service.audit_log import AuditLogService


class AuditLogController(BaseController):
    service_class = AuditLogService
    read_schema = AuditLogRead
    list_schema = AuditLogListItem
    query_schema = AuditLogQuery
