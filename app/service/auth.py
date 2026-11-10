"""Business rules for authentication: registration, login, sessions, passwords, and verification.

Rules:
- Refresh tokens rotate. If a used refresh token comes back, somebody copied it, so all sessions of the user stop.
- After login_max_failures failed logins in login_lockout_minutes, the account is locked for that time.
- Password-reset requests give the same answer for known and unknown users, so nobody can find accounts.
- A password change or reset stops all sessions.
"""

import datetime
import hmac
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.audit import current_audit_context, record_event
from app.core.actor import Actor
from app.core.config import settings
from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    InvalidInputError,
    TooManyAttemptsError,
    UnauthorizedError,
)
from app.core.security import (
    DUMMY_HASH,
    create_access_token,
    decode_access_token,
    hash_password,
    hash_token,
    new_numeric_code,
    new_random_token,
    verify_password,
)
from app.integration.notifier import Message, get_notifier
from app.model.enums import TokenPurpose
from app.model.user import User
from app.repository.audit_log import AuditLogRepository
from app.repository.auth_token import OneTimeTokenRepository, RefreshTokenRepository
from app.repository.consent import ConsentRecordRepository
from app.repository.user import UserRepository
from app.service.base import transaction
from app.service.role import require_role
from app.service.user import FARMER_ROLE, UserService
from app.util.time import utc_now

BAD_LOGIN = "The login or the password is not correct."
BAD_RESET = "The reset link is not valid or has expired. Ask for a new link."
LOGIN_FAILED = "auth.login_failed"
VERIFY_FAILED = "auth.verification_failed"
VERIFICATION = {  # Channel -> (token purpose, message channel, user address field, verified-at field)
    "email": (TokenPurpose.EMAIL_VERIFICATION, "email", "email", "email_verified_at"),
    "phone": (TokenPurpose.PHONE_VERIFICATION, "sms", "phone_number", "phone_verified_at"),
}


@dataclass(frozen=True)
class IssuedTokens:
    access_token: str
    refresh_token: str
    expires_in: int
    refresh_expires_at: datetime.datetime


def build_actor(user: User) -> Actor:  # The user as the services see it
    return Actor(
        id=user.id,
        username=user.username,
        roles=frozenset(role.name for role in user.roles),
        privileges=frozenset(p.code for role in user.roles for p in role.privileges),
    )


class AuthService:
    def __init__(self, db: Session, actor: Actor | None = None):
        self.db = db
        self.actor = actor
        self.users = UserRepository(db)
        self.refresh_tokens = RefreshTokenRepository(db)
        self.one_time_tokens = OneTimeTokenRepository(db)
        self.audit = AuditLogRepository(db)

    # Access tokens

    def actor_from_access_token(self, token: str) -> Actor:
        user = self.users.get_with_privileges(decode_access_token(token))
        if user is None or not user.is_active:  # Checked on each request, so a deactivation acts at once
            raise UnauthorizedError("The account does not exist or is deactivated.")
        return build_actor(user)

    # Registration and login

    def register(self, data: dict) -> User:
        consents = data.pop("consents", [])
        farmer_role = require_role(self.db, FARMER_ROLE)  # Before the slow password hash
        data["hashed_password"] = hash_password(data.pop("password"))
        data["email"] = data["email"].strip().lower()
        with transaction(self.db):
            user = self.users.create({**data, "roles": [farmer_role]})
            for consent_type in dict.fromkeys(consents):
                ConsentRecordRepository(self.db).create({
                    "user_id": user.id, "consent_type": consent_type, "granted": True,
                    "policy_version": settings.privacy_policy_version,
                })
            record_event(self.db, "auth.register", user, user_id=user.id)
            message = self._new_verification(user, "email")
        get_notifier().send(message)
        return self.users.get_with_privileges(user.id)

    def login(self, login: str, password: str) -> IssuedTokens:
        user = self.users.get_by_login(login)
        if user is None:
            verify_password(password, DUMMY_HASH)  # Same time as for a real user
            self._record_and_commit(LOGIN_FAILED, details={"login": login[:100]})
            raise UnauthorizedError(BAD_LOGIN)
        if self._recent_login_failures(user) >= settings.login_max_failures:
            raise TooManyAttemptsError(
                f"Too many failed logins. Try again in {settings.login_lockout_minutes} minutes,"
                " or reset the password."
            )
        if not verify_password(password, user.hashed_password):
            self._record_and_commit(LOGIN_FAILED, user=user)
            raise UnauthorizedError(BAD_LOGIN)
        if not user.is_active:  # Checked after the password, so the answer does not show which accounts exist
            raise ForbiddenError("The account is deactivated. Contact an administrator.")
        with transaction(self.db):
            user.last_login_at = self.audit.db_now()
            tokens = self._issue_tokens(user)
            record_event(self.db, "auth.login", user, user_id=user.id)
        return tokens

    def refresh(self, refresh_token: str) -> IssuedTokens:
        row = self.refresh_tokens.get_by_hash(hash_token(refresh_token))
        if row is None:
            raise UnauthorizedError("The refresh token is not valid. Log in again.")
        if row.revoked_at is not None:
            if row.replaced_by_id is not None:  # A rotated token came back, so a copy exists
                with transaction(self.db):
                    self._revoke_all(row.user_id)
                    record_event(self.db, "auth.refresh_token_reused", user_id=row.user_id)
            raise UnauthorizedError("The refresh token is not valid. Log in again.")
        if row.expires_at <= utc_now():
            raise UnauthorizedError("The refresh token has expired. Log in again.")
        user = self.users.get(row.user_id)
        if user is None or not user.is_active:
            raise UnauthorizedError("The account does not exist or is deactivated.")
        with transaction(self.db):
            tokens, new_row = self._issue_tokens(user, return_row=True)
            row.revoked_at = utc_now()
            row.replaced_by_id = new_row.id
        return tokens

    def logout(self, refresh_token: str) -> None:  # Same answer for a token that is not valid
        row = self.refresh_tokens.get_by_hash(hash_token(refresh_token))
        if row is None or row.revoked_at is not None:
            return
        with transaction(self.db):
            row.revoked_at = utc_now()
            record_event(self.db, "auth.logout", user_id=row.user_id)

    def logout_all(self) -> int:  # Stop all sessions of the logged-in user. Return the number stopped.
        with transaction(self.db):
            count = self._revoke_all(self._actor().id)
            record_event(self.db, "auth.logout_all", user_id=self._actor().id)
        return count

    # Account of the logged-in user

    def me(self) -> User:
        return self.users.get_with_privileges(self._actor().id)

    def update_me(self, data: dict) -> User:  # Internal call, so the users.update privilege is not necessary
        UserService(self.db).update(self._actor().id, data)
        return self.me()

    def change_password(self, current_password: str, new_password: str) -> IssuedTokens:
        user = self.me()
        if not verify_password(current_password, user.hashed_password):
            raise InvalidInputError("The current password is not correct.", {"fields": ["current_password"]})
        if verify_password(new_password, user.hashed_password):
            raise InvalidInputError("The new password must be different.", {"fields": ["new_password"]})
        with transaction(self.db):
            user.hashed_password = hash_password(new_password)
            self._revoke_all(user.id)  # Other devices must log in again
            record_event(self.db, "auth.password_changed", user, user_id=user.id)
            tokens = self._issue_tokens(user)  # This device stays logged in
        return tokens

    # Password reset

    def request_password_reset(self, login: str) -> None:
        user = self.users.get_by_login(login)
        if user is None or not user.is_active:
            return  # Same answer, so nobody can find accounts
        channel, address = ("email", user.email) if user.email else ("sms", user.phone_number)
        with transaction(self.db):
            token = self._new_one_time_token(user, TokenPurpose.PASSWORD_RESET, new_random_token())
            record_event(self.db, "auth.password_reset_requested", user, user_id=user.id)
        get_notifier().send(Message(
            user_id=user.id, channel=channel, address=address, subject="Reset your password",
            body=f"Use this token to reset your password. It expires in {settings.one_time_token_minutes} minutes.",
            token=token,
        ))

    def confirm_password_reset(self, token: str, new_password: str) -> None:
        row = self.one_time_tokens.get_by_hash(hash_token(token), TokenPurpose.PASSWORD_RESET)
        if row is None or row.used_at is not None or row.expires_at <= utc_now():
            raise InvalidInputError(BAD_RESET)
        user = self.users.get(row.user_id)
        if user is None or not user.is_active:
            raise InvalidInputError(BAD_RESET)
        with transaction(self.db):
            row.used_at = utc_now()
            user.hashed_password = hash_password(new_password)
            self._revoke_all(user.id)
            record_event(self.db, "auth.password_reset", user, user_id=user.id)

    # Verification of email and phone

    def request_verification(self, channel: str) -> None:
        user = self.me()
        with transaction(self.db):
            message = self._new_verification(user, channel)
        get_notifier().send(message)

    def confirm_verification(self, channel: str, code: str) -> User:
        user = self.me()
        purpose, _, _, verified_field = VERIFICATION[channel]
        now = utc_now()
        rows = [r for r in self.one_time_tokens.unused_for_user(user.id, purpose) if r.expires_at > now]
        if not rows:
            raise InvalidInputError("No code is active. Ask for a new code.")
        row = max(rows, key=lambda r: r.id)
        failures = self.audit.count_events(user.id, VERIFY_FAILED, row.created_at)
        if failures >= settings.verification_max_failures:
            with transaction(self.db):
                row.used_at = now  # The code stops working
            raise TooManyAttemptsError("Too many wrong codes. Ask for a new code.")
        if not hmac.compare_digest(hash_token(code.strip()), row.token_hash):
            self._record_and_commit(VERIFY_FAILED, user=user)
            raise InvalidInputError("The code is not correct.", {"fields": ["code"]})
        with transaction(self.db):
            row.used_at = now
            setattr(user, verified_field, now)
            record_event(self.db, f"auth.{channel}_verified", user, user_id=user.id)
        return self.me()

    # Helpers

    def _actor(self) -> Actor:
        if self.actor is None:
            raise UnauthorizedError("Log in first.")
        return self.actor

    def _issue_tokens(self, user: User, return_row: bool = False):
        access_token, expires_in = create_access_token(user.id)
        refresh_token = new_random_token()
        expires_at = utc_now() + datetime.timedelta(days=settings.refresh_token_days)
        context = current_audit_context()
        row = self.refresh_tokens.create({
            "user_id": user.id,
            "token_hash": hash_token(refresh_token),  # Only the hash is stored
            "expires_at": expires_at,
            "user_agent": context.user_agent if context else None,
            "ip_address": context.ip_address if context else None,
        })
        tokens = IssuedTokens(access_token, refresh_token, expires_in, expires_at)
        return (tokens, row) if return_row else tokens

    def _revoke_all(self, user_id: int) -> int:
        rows = self.refresh_tokens.active_for_user(user_id)
        now = utc_now()
        for row in rows:
            row.revoked_at = now
        self.db.flush()
        return len(rows)

    def _new_one_time_token(self, user: User, purpose: TokenPurpose, token: str) -> str:
        now = utc_now()
        for old in self.one_time_tokens.unused_for_user(user.id, purpose):
            old.used_at = now  # Only the newest token works
        self.one_time_tokens.create({
            "user_id": user.id,
            "purpose": purpose,
            "token_hash": hash_token(token),
            "expires_at": now + datetime.timedelta(minutes=settings.one_time_token_minutes),
        })
        return token

    def _new_verification(self, user: User, channel: str) -> Message:  # Call inside a transaction
        purpose, message_channel, address_field, verified_field = VERIFICATION[channel]
        address = getattr(user, address_field)
        if not address:
            raise InvalidInputError(f"Add a {address_field.replace('_', ' ')} to your account first.")
        if getattr(user, verified_field) is not None:
            raise ConflictError(f"The {channel} is already verified.")
        secret = new_numeric_code() if channel == "phone" else new_random_token()
        self._new_one_time_token(user, purpose, secret)
        return Message(
            user_id=user.id, channel=message_channel, address=address,
            subject=f"Verify your {channel}",
            body=f"Your code expires in {settings.one_time_token_minutes} minutes.",
            token=secret,
        )

    def _recent_login_failures(self, user: User) -> int:
        since = self.audit.db_now() - datetime.timedelta(minutes=settings.login_lockout_minutes)
        if user.last_login_at is not None and user.last_login_at > since:
            since = user.last_login_at  # A successful login resets the count
        return self.audit.count_events(user.id, LOGIN_FAILED, since)

    def _record_and_commit(self, action: str, user: User | None = None, details: dict | None = None) -> None:
        with transaction(self.db):  # Saved even though the request fails
            record_event(self.db, action, user, details=details, user_id=user.id if user else None)
