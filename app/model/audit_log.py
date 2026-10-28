from sqlalchemy import JSON, Column, DateTime, ForeignKey, Index, Integer, String, func  # Import column tools
from sqlalchemy.orm import relationship  # Import relationship
from app.database import Base  # Import Base


class AuditLog(Base):  # One row in the audit trail. Rows are never updated or deleted.
    __tablename__ = "audit_logs"  # Table name
    __table_args__ = (
        Index("ix_audit_logs_entity", "entity_type", "entity_id"),
    )  # Find the history of one record

    id = Column(Integer, primary_key=True, index=True)  # ID field
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )  # User who did the action, empty for system jobs
    action = Column(
        String(100), nullable=False, index=True
    )  # "insert", "update", "delete", or an event name such as "auth.login"
    entity_type = Column(String(50), nullable=True)  # Table name of the changed record
    entity_id = Column(Integer, nullable=True)  # ID of the changed record
    details = Column(
        JSON, nullable=True
    )  # {"changes": {column: {"old": ..., "new": ...}}} or event data, without secrets
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6 address
    user_agent = Column(String(255), nullable=True)  # Browser or device description
    request_id = Column(
        String(36), nullable=True, index=True
    )  # Groups all rows from one HTTP request
    created_at = Column(
        DateTime, nullable=False, server_default=func.now(), index=True
    )  # Time of the action

    user = relationship("User")  # Actor
