"""Schemas for login sessions and one-time tokens.

The API can list and revoke tokens. It cannot make or change them, and it never shows the token hash.
"""

from datetime import datetime

from app.model.enums import TokenPurpose
from app.schema.common import ListQuery, ReadSchema


class RefreshTokenRead(ReadSchema):
    id: int
    user_id: int
    expires_at: datetime
    revoked_at: datetime | None
    replaced_by_id: int | None
    user_agent: str | None
    ip_address: str | None
    created_at: datetime


class RefreshTokenQuery(ListQuery):
    user_id: int | None = None
    active: bool | None = None  # True: not revoked and not expired


class OneTimeTokenRead(ReadSchema):
    id: int
    user_id: int
    purpose: TokenPurpose
    expires_at: datetime
    used_at: datetime | None
    created_at: datetime


class OneTimeTokenQuery(ListQuery):
    user_id: int | None = None
    purpose: TokenPurpose | None = None
