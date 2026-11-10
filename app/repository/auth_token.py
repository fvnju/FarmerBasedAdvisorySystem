"""Database queries for login sessions and one-time tokens."""

from sqlalchemy import and_, or_, select

from app.model.auth_token import OneTimeToken, RefreshToken
from app.model.enums import TokenPurpose
from app.repository.base import BaseRepository
from app.repository.scope import OwnerScope
from app.util.time import utc_now


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    model = RefreshToken
    search_fields = (RefreshToken.user_agent, RefreshToken.ip_address)
    sort_fields = ("id", "created_at", "expires_at")

    def owner_condition(self, scope: OwnerScope):
        return scope.is_self(RefreshToken.user_id)  # An agent must not see the sessions of a farmer

    def filter_condition(self, name, value):
        if name == "active":
            now = utc_now()
            if value:
                return and_(RefreshToken.revoked_at.is_(None), RefreshToken.expires_at > now)
            return or_(RefreshToken.revoked_at.is_not(None), RefreshToken.expires_at <= now)
        return super().filter_condition(name, value)

    def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        return self.db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))

    def active_for_user(self, user_id: int) -> list[RefreshToken]:
        stmt = select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > utc_now(),
        )
        return list(self.db.scalars(stmt))


class OneTimeTokenRepository(BaseRepository[OneTimeToken]):
    model = OneTimeToken
    sort_fields = ("id", "created_at", "expires_at")

    def owner_condition(self, scope: OwnerScope):
        return scope.is_self(OneTimeToken.user_id)

    def get_by_hash(self, token_hash: str, purpose: TokenPurpose) -> OneTimeToken | None:
        stmt = select(OneTimeToken).where(
            OneTimeToken.token_hash == token_hash, OneTimeToken.purpose == purpose
        )
        return self.db.scalar(stmt)

    def unused_for_user(self, user_id: int, purpose: TokenPurpose) -> list[OneTimeToken]:
        stmt = select(OneTimeToken).where(
            OneTimeToken.user_id == user_id,
            OneTimeToken.purpose == purpose,
            OneTimeToken.used_at.is_(None),
        )
        return list(self.db.scalars(stmt))
