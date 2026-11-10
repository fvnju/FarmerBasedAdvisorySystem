"""Controller for authentication and the account of the logged-in user."""

from sqlalchemy.orm import Session

from app.core.actor import Actor
from app.schema.auth import (
    Accepted,
    ChangePasswordRequest,
    LoginRequest,
    MeRead,
    MeUpdate,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPair,
    VerificationConfirm,
    VerificationRequest,
)
from app.schema.user import UserRead
from app.service.auth import AuthService, IssuedTokens

RESET_ACCEPTED = "If the account exists, a reset message is on its way."


class AuthController:
    def __init__(self, db: Session, actor: Actor | None = None):
        self.service = AuthService(db, actor)

    def register(self, payload: RegisterRequest) -> MeRead:
        return self._me(self.service.register(payload.model_dump(exclude_unset=True)))

    def login(self, payload: LoginRequest) -> TokenPair:
        return self._tokens(self.service.login(payload.login, payload.password))

    def refresh(self, payload: RefreshRequest) -> TokenPair:
        return self._tokens(self.service.refresh(payload.refresh_token))

    def logout(self, payload: RefreshRequest) -> None:
        self.service.logout(payload.refresh_token)

    def logout_all(self) -> None:
        self.service.logout_all()

    def me(self) -> MeRead:
        return self._me(self.service.me())

    def update_me(self, payload: MeUpdate) -> MeRead:
        return self._me(self.service.update_me(payload.model_dump(exclude_unset=True)))

    def change_password(self, payload: ChangePasswordRequest) -> TokenPair:
        return self._tokens(self.service.change_password(payload.current_password, payload.new_password))

    def request_password_reset(self, payload: PasswordResetRequest) -> Accepted:
        self.service.request_password_reset(payload.login)
        return Accepted(detail=RESET_ACCEPTED)

    def confirm_password_reset(self, payload: PasswordResetConfirm) -> None:
        self.service.confirm_password_reset(payload.token, payload.new_password)

    def request_verification(self, payload: VerificationRequest) -> Accepted:
        self.service.request_verification(payload.channel.value)
        return Accepted(detail=f"A code is on its way to your {payload.channel.value}.")

    def confirm_verification(self, payload: VerificationConfirm) -> MeRead:
        return self._me(self.service.confirm_verification(payload.channel.value, payload.code))

    @staticmethod
    def _tokens(tokens: IssuedTokens) -> TokenPair:
        return TokenPair(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            expires_in=tokens.expires_in,
            refresh_expires_at=tokens.refresh_expires_at,
        )

    @staticmethod
    def _me(user) -> MeRead:
        return MeRead(
            **UserRead.model_validate(user).model_dump(),
            privileges=sorted({p.code for role in user.roles for p in role.privileges}),
            modules=sorted({m.name for role in user.roles for m in role.modules}),
        )
