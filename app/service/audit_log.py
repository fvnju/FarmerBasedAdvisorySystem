"""Business rules for the audit trail. The trail is read-only, so nobody can change the history."""

from app.model.audit_log import AuditLog
from app.repository.audit_log import AuditLogRepository
from app.schema.common import READ_ONLY
from app.service.base import BaseService


class AuditLogService(BaseService[AuditLog]):
    repository_class = AuditLogRepository
    operations = READ_ONLY
    label = "Audit log"
    module = "audit"
