"""Schemas that all resources share: list query, page, and delete-all result."""

import enum
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

MAX_PAGE_SIZE = 100  # Largest page that a client can ask for


class Operation(str, enum.Enum):  # Operations that a resource can support
    LIST = "list"
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    DELETE_ALL = "delete_all"


ALL_OPERATIONS = frozenset(Operation)
READ_ONLY = frozenset({Operation.LIST, Operation.READ})


class ReadSchema(BaseModel):  # Base for response schemas. Reads values from ORM objects.
    model_config = ConfigDict(from_attributes=True)


class ListQuery(BaseModel):  # Query parameters for list and search. Each resource adds its filters.
    model_config = ConfigDict(extra="forbid")

    page: int = Field(1, ge=1, description="Page number, starts at 1")
    size: int = Field(20, ge=1, le=MAX_PAGE_SIZE, description="Items on each page")
    q: str | None = Field(
        None,
        max_length=100,
        description="Search text. Send it again as the user types. The client must wait about 300 ms after the last key.",
    )
    sort: str = Field(
        "-id",
        pattern=r"^-?[a-z_]+$",
        description="Field to sort by. Put '-' before the name for descending order.",
    )
    include_total: bool = Field(
        True,
        description="Count all matches. Set to false for faster pages, for example in infinite scroll.",
    )

    def filters(self) -> dict:  # Filter values that the client set
        return self.model_dump(exclude=set(ListQuery.model_fields), exclude_none=True)


T = TypeVar("T")


class Page(BaseModel, Generic[T]):  # One page of results
    items: list[T]
    page: int
    size: int
    total: int | None = Field(None, description="All matches. Empty if include_total is false.")
    pages: int | None = Field(None, description="Number of pages. Empty if include_total is false.")
    has_next: bool


class DeleteAllResult(BaseModel):  # Result of a delete-all operation
    deleted: int
    skipped: int = Field(description="Records that other records still use, or that a rule protects")
