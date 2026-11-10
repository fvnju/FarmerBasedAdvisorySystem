"""Business rules for login sessions and one-time tokens.

The login and verification processes make the tokens. The API can only read and delete them.
A delete stops the session or the token at once. Users without data.all_farmers see only their own.
"""

from app.model.auth_token import OneTimeToken, RefreshToken
from app.repository.auth_token import OneTimeTokenRepository, RefreshTokenRepository
from app.schema.common import Operation
from app.service.base import BaseService

TOKEN_OPERATIONS = frozenset({Operation.LIST, Operation.READ, Operation.DELETE, Operation.DELETE_ALL})
SESSION_PERMISSIONS = {
    Operation.LIST: "sessions.read",
    Operation.READ: "sessions.read",
    Operation.DELETE: "sessions.revoke",
}


class RefreshTokenService(BaseService[RefreshToken]):
    repository_class = RefreshTokenRepository
    operations = TOKEN_OPERATIONS
    permissions = SESSION_PERMISSIONS
    label = "Login session"


class OneTimeTokenService(BaseService[OneTimeToken]):
    repository_class = OneTimeTokenRepository
    operations = TOKEN_OPERATIONS
    permissions = SESSION_PERMISSIONS
    label = "One-time token"
