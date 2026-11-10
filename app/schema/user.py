"""Schemas for users. The password hash is never in a response."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.schema.common import ListQuery, ReadSchema
from app.schema.fields import Email, Id, LanguageCode, Phone

USERNAME_PATTERN = r"^[A-Za-z0-9_.-]+$"


class RoleBrief(ReadSchema):
    id: int
    name: str


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=USERNAME_PATTERN)
    email: Email
    password: str = Field(min_length=8, max_length=128)
    phone_number: Phone | None = None
    full_name: str | None = Field(None, max_length=150)
    preferred_language: LanguageCode = "en"
    is_active: bool = True
    role_ids: list[Id] = Field(default_factory=list)


class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=50, pattern=USERNAME_PATTERN)
    email: Email | None = None
    password: str | None = Field(None, min_length=8, max_length=128)
    phone_number: Phone | None = None
    full_name: str | None = Field(None, max_length=150)
    preferred_language: LanguageCode | None = None
    is_active: bool | None = None
    role_ids: list[Id] | None = None


class UserRead(ReadSchema):
    id: int
    username: str
    email: str
    phone_number: str | None
    full_name: str | None
    preferred_language: str
    is_active: bool
    email_verified_at: datetime | None
    phone_verified_at: datetime | None
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime
    roles: list[RoleBrief]


class UserQuery(ListQuery):
    is_active: bool | None = None
    role_id: int | None = None
