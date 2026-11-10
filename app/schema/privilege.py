"""Schemas for privileges."""

from pydantic import BaseModel, Field

from app.schema.common import ListQuery, ReadSchema
from app.schema.fields import Id

PRIVILEGE_CODE = r"^[a-z_]+\.[a-z_]+$"


class PrivilegeCreate(BaseModel):
    module_id: Id
    code: str = Field(
        max_length=100, pattern=PRIVILEGE_CODE, description="'<module>.<action>', for example 'farms.update'"
    )
    description: str | None = Field(None, max_length=255)


class PrivilegeUpdate(BaseModel):
    module_id: Id | None = None
    code: str | None = Field(None, max_length=100, pattern=PRIVILEGE_CODE)
    description: str | None = Field(None, max_length=255)


class PrivilegeRead(ReadSchema):
    id: int
    module_id: int
    code: str
    description: str | None


class PrivilegeQuery(ListQuery):
    module_id: int | None = None
