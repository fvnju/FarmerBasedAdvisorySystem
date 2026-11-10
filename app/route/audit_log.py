"""Routes for audit logs."""

from app.controller.audit_log import AuditLogController
from app.route.factory import build_crud_router

router = build_crud_router(AuditLogController, prefix="/audit-logs", tag="Audit logs")
