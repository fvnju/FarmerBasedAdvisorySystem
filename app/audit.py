import contextvars  # Import contextvars to keep the actor for each request
import datetime  # Import datetime to convert dates to text
import decimal  # Import decimal to convert Numeric values
import enum  # Import enum to convert enum values
import uuid  # Import uuid to make request IDs
from dataclasses import dataclass, field  # Import dataclass for the audit context

from sqlalchemy import event, inspect  # Import event hooks and the inspector
from sqlalchemy.orm import Session  # Import Session to attach the hook

from app.model.audit_log import AuditLog  # Import the audit table

EXCLUDED_TABLES = {
    "audit_logs",  # The trail must not audit itself
    "refresh_tokens",  # Login sessions change often. Use record_event for login and logout.
    "one_time_tokens",  # Secrets with a short life
    "document_chunks",  # Large text and embeddings, made again from the document
    "weather_forecasts",  # System data from the provider, rows are never updated
}  # Tables that the trail does not record

IGNORED_COLUMNS = {"created_at", "updated_at"}  # Columns that change on each write
REDACTED_COLUMNS = {"hashed_password", "token_hash"}  # Record that they changed, not the value
REDACTED = "***"  # Value written for a redacted column


@dataclass
class AuditContext:  # Who does the actions in the current request
    user_id: int | None = None  # Set by the authentication dependency
    ip_address: str | None = None  # Set by the middleware
    user_agent: str | None = None  # Set by the middleware
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))  # Groups the rows of one request


_audit_context = contextvars.ContextVar("audit_context", default=None)  # Context of the current request


def start_audit_context(ip_address=None, user_agent=None):  # Start a new context, for example in middleware
    context = AuditContext(ip_address=ip_address, user_agent=(user_agent or "")[:255] or None)
    return context, _audit_context.set(context)


def end_audit_context(token):  # Remove the context at the end of the request
    _audit_context.reset(token)


def set_audit_user(user_id):  # Call this after authentication
    context = _audit_context.get()
    if context is not None:
        context.user_id = user_id  # Change the object, so threads that copied the context also see it


def _to_json(value):  # Convert a column value to a value that JSON can keep
    if isinstance(value, enum.Enum):
        return value.value
    if isinstance(value, (datetime.date, datetime.datetime, datetime.time)):
        return value.isoformat()
    if isinstance(value, decimal.Decimal):
        return str(value)
    return value


def _entity_id(obj):  # Primary key of a record, if it is one integer
    key = inspect(obj).mapper.primary_key_from_instance(obj)
    return key[0] if len(key) == 1 and isinstance(key[0], int) else None


def _column_value(key, value):  # Value to write for one column
    return REDACTED if key in REDACTED_COLUMNS and value is not None else _to_json(value)


def _snapshot(obj):  # All column values of a record
    state = inspect(obj)
    return {
        attr.key: _column_value(attr.key, getattr(obj, attr.key))
        for attr in state.mapper.column_attrs
        if attr.key not in IGNORED_COLUMNS
    }


def _changes(obj):  # Changed columns and many-to-many links of a record
    state = inspect(obj)
    changes = {}
    for attr in state.mapper.column_attrs:
        if attr.key in IGNORED_COLUMNS:
            continue
        history = state.attrs[attr.key].history
        if not history.has_changes():
            continue
        old = history.deleted[0] if history.deleted else None
        new = history.added[0] if history.added else None
        changes[attr.key] = {"old": _column_value(attr.key, old), "new": _column_value(attr.key, new)}
    for rel in state.mapper.relationships:
        if rel.secondary is None:
            continue  # Other relationships show as a foreign key column on the child record
        history = state.attrs[rel.key].history
        if history.added or history.deleted:
            changes[rel.key] = {
                "added": [_entity_id(o) for o in history.added],
                "removed": [_entity_id(o) for o in history.deleted],
            }
    return changes


def _row(context, action, obj, details):  # One audit_logs row as a dict
    return {
        "user_id": context.user_id if context else None,
        "action": action,
        "entity_type": obj.__table__.name,
        "entity_id": _entity_id(obj),
        "details": details,
        "ip_address": context.ip_address if context else None,
        "user_agent": context.user_agent if context else None,
        "request_id": context.request_id if context else None,
    }


def _after_flush(session, flush_context):  # Write the audit rows in the same transaction
    context = _audit_context.get()
    rows = []
    for obj in session.new:
        if obj.__table__.name not in EXCLUDED_TABLES:
            rows.append(_row(context, "insert", obj, {"changes": {k: {"old": None, "new": v} for k, v in _snapshot(obj).items()}}))
    for obj in session.dirty:
        if obj.__table__.name not in EXCLUDED_TABLES and session.is_modified(obj):
            changes = _changes(obj)
            if changes:
                rows.append(_row(context, "update", obj, {"changes": changes}))
    for obj in session.deleted:
        if obj.__table__.name not in EXCLUDED_TABLES:
            rows.append(_row(context, "delete", obj, {"changes": {k: {"old": v, "new": None} for k, v in _snapshot(obj).items()}}))
    if rows:
        session.connection().execute(AuditLog.__table__.insert(), rows)  # Core insert, because the flush is in progress


def record_event(db, action, entity=None, details=None, user_id=None):  # Record an event that is not a row change
    context = _audit_context.get()
    db.add(
        AuditLog(
            user_id=user_id if user_id is not None else (context.user_id if context else None),
            action=action,  # For example "auth.login", "auth.login_failed", or "farms.export"
            entity_type=entity.__table__.name if entity is not None else None,
            entity_id=_entity_id(entity) if entity is not None else None,
            details=details,
            ip_address=context.ip_address if context else None,
            user_agent=context.user_agent if context else None,
            request_id=context.request_id if context else None,
        )
    )


def register_audit_listeners():  # Call one time when the app starts
    if not event.contains(Session, "after_flush", _after_flush):
        event.listen(Session, "after_flush", _after_flush)
