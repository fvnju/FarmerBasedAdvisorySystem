"""Base controller. It connects the HTTP layer to the service layer.

A controller:
- converts request schemas to plain data for the service,
- calls the service,
- converts ORM objects to response schemas.
It does not query the database and does not contain business rules.
"""

import math
from typing import ClassVar

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.actor import Actor
from app.schema.common import DeleteAllResult, ListQuery, Operation, Page
from app.service.base import BaseService


class BaseController:
    service_class: ClassVar[type[BaseService]]
    read_schema: ClassVar[type[BaseModel]]  # Response for one record
    list_schema: ClassVar[type[BaseModel] | None] = None  # Response for each item in a page. None means read_schema.
    create_schema: ClassVar[type[BaseModel] | None] = None  # Body for insert. None if the resource has no insert.
    update_schema: ClassVar[type[BaseModel] | None] = None  # Body for update. None if the resource has no update.
    query_schema: ClassVar[type[ListQuery]] = ListQuery  # Query parameters for list and search

    def __init__(self, db: Session, actor: Actor | None = None):
        self.service = self.service_class(db, actor)  # The service checks the privileges of the actor

    @classmethod
    def operations(cls) -> frozenset[Operation]:  # Operations that the router must show
        return cls.service_class.operations

    @classmethod
    def item_schema(cls) -> type[BaseModel]:
        return cls.list_schema or cls.read_schema

    def list(self, query: ListQuery) -> Page:
        result = self.service.list(
            page=query.page,
            size=query.size,
            q=query.q,
            filters=query.filters(),
            sort=query.sort,
            include_total=query.include_total,
        )
        schema = self.item_schema()
        return Page[schema](
            items=[schema.model_validate(item) for item in result.items],
            page=result.page,
            size=result.size,
            total=result.total,
            pages=math.ceil(result.total / result.size) if result.total is not None else None,
            has_next=result.has_next,
        )

    def get(self, item_id: int) -> BaseModel:
        return self.to_read(self.service.get(item_id))

    def create(self, payload: BaseModel) -> BaseModel:
        return self.to_read(self.service.create(payload.model_dump(exclude_unset=True)))

    def update(self, item_id: int, payload: BaseModel) -> BaseModel:
        return self.to_read(self.service.update(item_id, payload.model_dump(exclude_unset=True)))

    def delete(self, item_id: int) -> None:
        self.service.delete(item_id)

    def delete_all(self, confirm: bool) -> DeleteAllResult:
        deleted, skipped = self.service.delete_all(confirm)
        return DeleteAllResult(deleted=deleted, skipped=skipped)

    def to_read(self, item) -> BaseModel:
        return self.read_schema.model_validate(item)
