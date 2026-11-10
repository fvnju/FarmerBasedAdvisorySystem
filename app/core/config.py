"""Application settings. Values come from the environment or from the .env file."""

import logging
import secrets

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    jwt_secret: str | None = None  # Set JWT_SECRET in production. At least 32 random characters.
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 15  # Short life, because the server cannot revoke an access token
    refresh_token_days: int = 14
    one_time_token_minutes: int = 30  # Life of a password-reset or verification token
    login_max_failures: int = 5  # Failed logins before the account is locked for a time
    login_lockout_minutes: int = 15
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]  # React dev servers
    seed_admin_password: str | None = None
    privacy_policy_version: str = "1.0"  # Version of the privacy text that registration shows
    verification_max_failures: int = 5  # Wrong codes before a verification code stops working


settings = Settings()

if not settings.jwt_secret:
    settings.jwt_secret = secrets.token_urlsafe(48)
    logger.warning(
        "JWT_SECRET is not set. A random secret is used, so all tokens stop working when the server restarts."
    )
