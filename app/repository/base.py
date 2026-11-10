"""Base repository. It is the only layer that builds SQL queries.

A repository does not commit. The service controls the transaction.
Each query takes an optional scope condition, which limits the rows to the data of the logged-in user.
"""

from typing import Any, ClassVar, Generic, TypeVar

from sqlalchemy import ColumnElement, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repository.scope import OwnerScope

ModelT = TypeVar("ModelT")

LIKE_ESCAPE = "/"  # Escape character for LIKE. A backslash causes problems in MySQL literals.


def like_pattern(text: str) -> str:  # "%text%" with the LIKE wildcards in the text escaped
    escaped = (
        text.replace(LIKE_ESCAPE, LIKE_ESCAPE * 2)
        .replace("%", LIKE_ESCAPE + "%")
        .replace("_", LIKE_ESCAPE + "_")
    )
    return f"%{escaped}%"


def integrity_message(error: IntegrityError) -> str:  # Text for the client from a database error
    original = getattr(error, "orig", None)
    args = getattr(original, "args", ())
    mysql_code = args[0] if args and isinstance(args[0], int) else None
    pg_code = getattr(original, "pgcode", None)
    if mysql_code == 1062 or pg_code == "23505":
        return "A record with the same unique value already exists."
    if mysql_code == 1452:
        return "A linked record does not exist. Check the ID fields."
    if mysql_code == 1451:
        return "Other records use this record. Delete or change them first."
    if pg_code == "23503":
        return "A linked record does not exist, or other records use this record."
    if mysql_code == 1048 or pg_code == "23502":
        return "A required field is empty."
    text = str(original).lower()  # Other databases, for example SQLite in tests
    if "unique" in text or "duplicate" in text:
        return "A record with the same unique value already exists."
    if "foreign key" in text:
        return "A linked record does not exist, or other records use this record."
    return "The change breaks a database rule."


Scope = ColumnElement | None  # Extra condition from the data scope. None means all rows.


class BaseRepository(Generic[ModelT]):
    model: ClassVar[type]  # ORM class
    search_fields: ClassVar[tuple] = ()  # Text columns that the search text looks in
    sort_fields: ClassVar[tuple[str, ...]] = ("id",)  # Columns that a client can sort by
    load_options: ClassVar[tuple] = ()  # Loader options for one record, for example selectinload
    list_options: ClassVar[tuple | None] = None  # Loader options for a page. None means load_options.

    def __init__(self, db: Session):
        self.db = db

    # Data scope

    def owner_condition(self, scope: OwnerScope) -> ColumnElement | None:
        """Condition that limits the rows to the data of the scope. None if the rows have no owner."""
        return None

    # Queries

    def get(self, item_id: int, scope: Scope = None) -> ModelT | None:
        if scope is None:
            return self.db.get(self.model, item_id, options=list(self.load_options))
        stmt = select(self.model).where(self.model.id == item_id, scope).options(*self.load_options)
        return self.db.scalar(stmt)

    def get_many(self, ids: list[int]) -> list[ModelT]:  # Records with the given IDs, in any order
        if not ids:
            return []
        return list(self.db.scalars(select(self.model).where(self.model.id.in_(ids))))

    def exists(self, item_id: int, scope: Scope = None) -> bool:
        conditions = [self.model.id == item_id] + ([scope] if scope is not None else [])
        return self.db.scalar(select(self.model.id).where(*conditions)) is not None

    def list(
        self,
        *,
        offset: int,
        limit: int,
        q: str | None = None,
        filters: dict[str, Any] | None = None,
        sort: str = "-id",
        scope: Scope = None,
    ) -> list[ModelT]:
        options = self.load_options if self.list_options is None else self.list_options
        stmt = (
            select(self.model)
            .where(*self._conditions(q, filters or {}, scope))
            .options(*options)
            .order_by(*self._order_by(sort))
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(stmt))

    def count(self, *, q: str | None = None, filters: dict[str, Any] | None = None, scope: Scope = None) -> int:
        stmt = select(func.count(self.model.id)).where(*self._conditions(q, filters or {}, scope))
        return self.db.scalar(stmt) or 0

    def batch_after(self, last_id: int, limit: int, scope: Scope = None) -> list[ModelT]:
        """Next records by ID. Safe while rows are deleted."""
        conditions = [self.model.id > last_id] + ([scope] if scope is not None else [])
        stmt = select(self.model).where(*conditions).order_by(self.model.id).limit(limit)
        return list(self.db.scalars(stmt))

    # Changes. They flush, so database errors occur here and not at commit.

    def create(self, data: dict[str, Any]) -> ModelT:
        item = self.model(**data)
        self.db.add(item)
        self.db.flush()
        return item

    def update(self, item: ModelT, data: dict[str, Any]) -> ModelT:
        for key, value in data.items():
            setattr(item, key, value)
        self.db.flush()
        return item

    def delete(self, item: ModelT) -> None:  # ORM delete, so the audit trail and the cascades run
        self.db.delete(item)
        self.db.flush()

    # Query parts. A subclass can change them.

    def search_condition(self, pattern: str) -> ColumnElement | None:  # Condition for the search text
        if not self.search_fields:
            return None
        return or_(*(column.ilike(pattern, escape=LIKE_ESCAPE) for column in self.search_fields))

    def filter_condition(self, name: str, value: Any) -> ColumnElement:  # Condition for one filter
        return getattr(self.model, name) == value

    def _conditions(self, q: str | None, filters: dict[str, Any], scope: Scope) -> list[ColumnElement]:
        conditions = [self.filter_condition(name, value) for name, value in filters.items()]
        if q:
            condition = self.search_condition(like_pattern(q))
            if condition is not None:
                conditions.append(condition)
        if scope is not None:
            conditions.append(scope)
        return conditions

    def _order_by(self, sort: str) -> list:  # The service checks the field before this call
        descending = sort.startswith("-")
        column = getattr(self.model, sort.lstrip("-"))
        order = [column.desc() if descending else column.asc()]
        if sort.lstrip("-") != "id":
            order.append(self.model.id.desc() if descending else self.model.id.asc())  # Stable order between pages
        return order
