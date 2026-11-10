"""Schemas for crops."""

from pydantic import BaseModel, Field

from app.schema.common import ListQuery, ReadSchema


class CropCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    scientific_name: str | None = Field(None, max_length=150)
    is_supported: bool = False


class CropUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    scientific_name: str | None = Field(None, max_length=150)
    is_supported: bool | None = None


class CropRead(ReadSchema):
    id: int
    name: str
    scientific_name: str | None
    is_supported: bool


class CropQuery(ListQuery):
    is_supported: bool | None = None
