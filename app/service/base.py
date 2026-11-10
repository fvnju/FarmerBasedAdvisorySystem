"""Base service. It holds the business rules, the access rules, and the transaction.

A service does not know about HTTP or about the response schemas.
It gets plain data, returns ORM objects, and raises the errors in app/core/exceptions.py.

Access rules:
1. Each operation needs a privilege. See permission_for. A service without a privilege refuses the request.
2. A user without data.all_farmers sees only their own data and the data of their assigned farmers.
   The repository gives this condition in owner_condition.
3. actor is None only for internal calls, for example the seed. Internal calls skip the access rules.
"""

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, ClassVar, Generic, Iterator, TypeVar

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.actor import Actor
from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    InvalidInputError,
    NotFoundError,
    OperationNotAllowedError,
)
from app.repository.base import BaseRepository, Scope, integrity_message
from app.repository.scope import OwnerScope
from app.schema.common import ALL_OPERATIONS, Operation
from app.util.time import utc_today

ModelT = TypeVar("ModelT")

DELETE_BATCH_SIZE = 500  # Records loaded at one time during delete-all
DELETE_ALL_PRIVILEGE = "system.delete_all"
DEFAULT_ACTIONS = {  # Operation -> action part of the privilege code
    Operation.LIST: "read",
    Operation.READ: "read",
    Operation.CREATE: "create",
    Operation.UPDATE: "update",
    Operation.DELETE: "delete",
}
OUT_OF_SCOPE = "You can only use the records of your own farms or of the farmers assigned to you."


@dataclass
class PageResult(Generic[ModelT]):  # One page of ORM objects
    items: list[ModelT]
    page: int
    size: int
    total: int | None
    has_next: bool


class Values:  # The new value of a field if the change sets it, else the current value
    def __init__(self, data: dict[str, Any], current: Any | None):
        self.data = data
        self.current = current

    def __getitem__(self, key: str) -> Any:
        if key in self.data:
            return self.data[key]
        return getattr(self.current, key, None) if self.current is not None else None

    def changed(self, key: str) -> bool:  # True if the change gives the field a different value
        if key not in self.data:
            return False
        return self.current is None or getattr(self.current, key, None) != self.data[key]


class BaseService(Generic[ModelT]):
    repository_class: ClassVar[type[BaseRepository]]
    operations: ClassVar[frozenset[Operation]] = ALL_OPERATIONS
    label: ClassVar[str] = "Record"  # Name of the resource in messages
    module: ClassVar[str | None] = None  # Module part of the privilege codes, for example "farms"
    permissions: ClassVar[dict[Operation, str]] = {}  # Privileges that are not "<module>.<action>"
    actor_fields: ClassVar[tuple[str, ...]] = ()  # Fields set to the logged-in user on insert

    def __init__(self, db: Session, actor: Actor | None = None):
        self.db = db
        self.actor = actor
        self.repo = self.repository_class(db)

    # Hooks. A subclass changes these to add its business rules.

    def prepare(self, data: dict[str, Any], current: ModelT | None) -> dict[str, Any]:
        """Change the input before it is saved, for example hash a password. current is None for a create."""
        return data

    def validate(self, values: Values, current: ModelT | None) -> None:
        """Raise InvalidInputError if the record breaks a rule. values holds the new and current values."""

    def check_delete(self, item: ModelT) -> str | None:
        """Return the reason the record must not be deleted, or None."""
        return None

    def after_save(self, item: ModelT, created: bool) -> None:
        """Change related records in the same transaction."""

    # Operations

    def get(self, item_id: int) -> ModelT:
        self._require(Operation.READ)
        return self._find(item_id)

    def list(
        self,
        *,
        page: int,
        size: int,
        q: str | None,
        filters: dict[str, Any],
        sort: str,
        include_total: bool,
    ) -> PageResult[ModelT]:
        self._require(Operation.LIST)
        field = sort.lstrip("-")
        if field not in self.repo.sort_fields:
            raise InvalidInputError(
                f"You cannot sort by '{field}'.", {"allowed": list(self.repo.sort_fields)}
            )
        q = q.strip() if q else None
        scope = self._scope()
        rows = self.repo.list(
            offset=(page - 1) * size, limit=size + 1, q=q, filters=filters, sort=sort, scope=scope
        )  # One more row than the page shows that a next page exists, without a count
        total = self.repo.count(q=q, filters=filters, scope=scope) if include_total else None
        return PageResult(
            items=rows[:size], page=page, size=size, total=total, has_next=len(rows) > size
        )

    def create(self, data: dict[str, Any]) -> ModelT:
        self._require(Operation.CREATE)
        data = self._fill_actor_fields(dict(data))
        data = self.prepare(data, None)
        self._reject_empty_required(data)
        self.validate(Values(data, None), None)
        with self._transaction():
            item = self.repo.create(data)
            self.after_save(item, created=True)
            self._check_in_scope(item)  # Before the commit, so a record of another farmer is rolled back
        return item

    def update(self, item_id: int, data: dict[str, Any]) -> ModelT:
        self._require(Operation.UPDATE)
        if not data:
            raise InvalidInputError("Give at least one field to change.")
        item = self._find(item_id)
        data = self.prepare(dict(data), item)
        self._reject_empty_required(data)
        self.validate(Values(data, item), item)
        with self._transaction():
            self.repo.update(item, data)
            self.after_save(item, created=False)
            self._check_in_scope(item)  # The change must not move the record to another farmer
        return item

    def delete(self, item_id: int) -> None:
        self._require(Operation.DELETE)
        item = self._find(item_id)
        reason = self.check_delete(item)
        if reason:
            raise ConflictError(reason)
        with self._transaction():
            self.repo.delete(item)

    def delete_all(self, confirm: bool) -> tuple[int, int]:  # Return (deleted, skipped)
        self._require(Operation.DELETE_ALL)
        if not confirm:
            raise InvalidInputError("Set confirm to true to delete all records.")
        deleted = skipped = 0
        last_id = 0
        scope = self._scope()
        with self._transaction():
            while batch := self.repo.batch_after(last_id, DELETE_BATCH_SIZE, scope):
                for item in batch:
                    last_id = item.id
                    if self.check_delete(item):
                        skipped += 1
                        continue
                    try:
                        with self.db.begin_nested():  # A savepoint, so one failed row does not stop the others
                            self.repo.delete(item)
                        deleted += 1
                    except IntegrityError:
                        skipped += 1  # Other records still use this record
        return deleted, skipped

    # Access rules

    @classmethod
    def permission_for(cls, operation: Operation) -> str | None:  # Privilege code for an operation
        if operation in cls.permissions:
            return cls.permissions[operation]
        if operation == Operation.DELETE_ALL:
            return DELETE_ALL_PRIVILEGE
        if cls.module is None:
            return None
        return f"{cls.module}.{DEFAULT_ACTIONS[operation]}"

    def _require(self, operation: Operation) -> None:
        if operation not in self.operations:
            raise OperationNotAllowedError(
                f"{self.label}: the operation '{operation.value}' is not permitted."
            )
        if self.actor is None:
            return
        code = self.permission_for(operation)
        if code is None:  # Fail closed: a service that names no privilege is not open to all users
            raise ForbiddenError(f"{self.label}: no privilege gives access to this operation.")
        self._require_privilege(code)

    def _require_privilege(self, code: str) -> None:
        if self.actor is not None and not self.actor.has(code):
            raise ForbiddenError(f"You need the privilege '{code}'.", {"privilege": code})

    @property
    def is_scoped(self) -> bool:  # True if the user sees only their own data
        return self.actor is not None and not self.actor.unrestricted

    def _scope(self) -> Scope:
        if not self.is_scoped:
            return None
        return self.repo.owner_condition(OwnerScope(self.actor.id))

    def _check_in_scope(self, item: ModelT) -> None:
        scope = self._scope()
        if scope is not None and not self.repo.exists(item.id, scope):
            raise ForbiddenError(OUT_OF_SCOPE)

    def _fill_actor_fields(self, data: dict[str, Any]) -> dict[str, Any]:
        if self.actor is None:
            return data
        for field in self.actor_fields:
            if self.is_scoped or data.get(field) is None:  # A scoped user cannot name another user
                data[field] = self.actor.id
        return data

    # Helpers

    def _find(self, item_id: int) -> ModelT:  # A record outside the scope gives "does not exist"
        item = self.repo.get(item_id, self._scope())
        if item is None:
            raise NotFoundError(f"{self.label} {item_id} does not exist.")
        return item

    def _get_linked(self, repository: BaseRepository, item_id: int, label: str):  # A linked record, or NotFoundError
        item = repository.get(item_id)
        if item is None:
            raise NotFoundError(f"{label} {item_id} does not exist.")
        return item

    def _load_many(self, repository: BaseRepository, ids: list[int] | None, label: str) -> list:
        ids = list(dict.fromkeys(ids or []))  # Remove duplicates, keep the order
        items = repository.get_many(ids)
        missing = sorted(set(ids) - {item.id for item in items})
        if missing:
            raise NotFoundError(f"Some {label} records do not exist.", {"ids": missing})
        return items

    @staticmethod
    def _require_values(values: Values, fields: list[str], message: str) -> None:  # Stop empty values for a rule
        missing = [field for field in fields if values[field] in (None, "", [], {})]
        if missing:
            raise InvalidInputError(message, {"fields": missing})

    @staticmethod
    def _not_in_future(values: Values, *fields: str) -> None:  # Dates that must not be after today
        for field in fields:
            value = values[field]
            if values.changed(field) and value is not None and value > utc_today():
                raise InvalidInputError(f"{field} must not be in the future.", {"fields": [field]})

    def _reject_empty_required(self, data: dict[str, Any]) -> None:  # Stop null in a NOT NULL column
        columns = self.repo.model.__table__.c
        empty = [
            key for key, value in data.items()
            if value is None and key in columns and not columns[key].nullable
        ]
        if empty:
            raise InvalidInputError("These fields must not be empty.", {"fields": empty})

    def _transaction(self):
        return transaction(self.db)


@contextmanager
def transaction(db: Session) -> Iterator[None]:  # Commit at the end, or roll back on an error
    try:
        yield
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ConflictError(integrity_message(error)) from error
    except Exception:
        db.rollback()
        raise
