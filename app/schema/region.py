"""Schemas for regions."""

from pydantic import BaseModel, Field

from app.schema.common import ListQuery, ReadSchema


class RegionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    is_supported: bool = False


class RegionUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    is_supported: bool | None = None


class RegionRead(ReadSchema):
    id: int
    name: str
    description: str | None
    is_supported: bool


class RegionQuery(ListQuery):
    is_supported: bool | None = None
