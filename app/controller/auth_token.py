"""Controllers for login sessions, one-time tokens."""

from app.controller.base import BaseController
from app.schema.auth_token import (
    OneTimeTokenQuery,
    OneTimeTokenRead,
    RefreshTokenQuery,
    RefreshTokenRead,
)
from app.service.auth_token import (
    OneTimeTokenService,
    RefreshTokenService,
)


class RefreshTokenController(BaseController):
    service_class = RefreshTokenService
    read_schema = RefreshTokenRead
    query_schema = RefreshTokenQuery


class OneTimeTokenController(BaseController):
    service_class = OneTimeTokenService
    read_schema = OneTimeTokenRead
    query_schema = OneTimeTokenQuery
