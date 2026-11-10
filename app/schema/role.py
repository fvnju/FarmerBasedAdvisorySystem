"""Schemas for roles."""

from pydantic import BaseModel, Field

from app.schema.common import ListQuery, ReadSchema
from app.schema.fields import Id


class ModuleBrief(ReadSchema):
    id: int
    name: str


class PrivilegeBrief(ReadSchema):
    id: int
    code: str


class RoleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50, pattern=r"^[a-z_]+$")
    description: str | None = Field(None, max_length=255)
    module_ids: list[Id] = Field(default_factory=list)
    privilege_ids: list[Id] = Field(
        default_factory=list, description="The modules of these privileges are added to the role"
    )


class RoleUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50, pattern=r"^[a-z_]+$")
    description: str | None = Field(None, max_length=255)
    module_ids: list[Id] | None = None
    privilege_ids: list[Id] | None = None


class RoleRead(ReadSchema):
    id: int
    name: str
    description: str | None
    is_system: bool
    modules: list[ModuleBrief]
    privileges: list[PrivilegeBrief]


class RoleQuery(ListQuery):
    is_system: bool | None = None
