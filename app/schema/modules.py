"""Schemas for modules."""

from pydantic import BaseModel, Field

from app.schema.common import ListQuery, ReadSchema

MODULE_NAME = r"^[a-z_]+$"


class ModuleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50, pattern=MODULE_NAME)
    description: str | None = Field(None, max_length=255)


class ModuleUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50, pattern=MODULE_NAME)
    description: str | None = Field(None, max_length=255)


class ModuleRead(ReadSchema):
    id: int
    name: str
    description: str | None


class ModuleQuery(ListQuery):
    pass
