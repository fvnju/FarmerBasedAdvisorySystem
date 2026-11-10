"""Password hashes, access tokens (JWT), and random tokens.

Refresh tokens and one-time tokens are random strings. The database keeps only their SHA-256 hash.
"""

import base64
import datetime
import hashlib
import hmac
import secrets
import uuid

import jwt

from app.core.config import settings
from app.core.exceptions import UnauthorizedError

_N, _R, _P = 2**14, 8, 1  # scrypt cost values
_SALT_BYTES = 16
_PREFIX = "scrypt"
_ACCESS = "access"


# Passwords


def hash_password(password: str) -> str:  # Return "scrypt$<salt>$<hash>"
    salt = secrets.token_bytes(_SALT_BYTES)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=_N, r=_R, p=_P)
    return "$".join(
        [_PREFIX, base64.b64encode(salt).decode(), base64.b64encode(digest).decode()]
    )


def verify_password(password: str, hashed: str) -> bool:  # True if the password agrees with the hash
    try:
        prefix, salt_text, digest_text = hashed.split("$")
    except ValueError:
        return False
    if prefix != _PREFIX:
        return False
    salt = base64.b64decode(salt_text)
    expected = base64.b64decode(digest_text)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=_N, r=_R, p=_P)
    return hmac.compare_digest(digest, expected)


DUMMY_HASH = hash_password(secrets.token_urlsafe(16))  # Checked for unknown users, so the time is the same


# Access tokens


def create_access_token(user_id: int) -> tuple[str, int]:  # Return (token, seconds until it expires)
    now = datetime.datetime.now(datetime.UTC)
    lifetime = datetime.timedelta(minutes=settings.access_token_minutes)
    claims = {
        "sub": str(user_id),
        "typ": _ACCESS,
        "iat": now,
        "exp": now + lifetime,
        "jti": str(uuid.uuid4()),
    }
    token = jwt.encode(claims, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, int(lifetime.total_seconds())


def decode_access_token(token: str) -> int:  # Return the user ID, or raise UnauthorizedError
    try:
        claims = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],  # Never accept the algorithm that the token names
            options={"require": ["sub", "exp", "iat", "typ"]},
        )
    except jwt.ExpiredSignatureError as error:
        raise UnauthorizedError("The access token has expired. Use the refresh token.") from error
    except jwt.InvalidTokenError as error:
        raise UnauthorizedError("The access token is not valid.") from error
    if claims.get("typ") != _ACCESS or not str(claims["sub"]).isdigit():
        raise UnauthorizedError("The access token is not valid.")
    return int(claims["sub"])


# Random tokens


def new_random_token() -> str:  # For refresh tokens and links in emails
    return secrets.token_urlsafe(32)


def new_numeric_code(digits: int = 6) -> str:  # For SMS codes
    return str(secrets.randbelow(10**digits)).zfill(digits)


def hash_token(token: str) -> str:  # SHA-256, which is enough for random tokens
    return hashlib.sha256(token.encode()).hexdigest()
