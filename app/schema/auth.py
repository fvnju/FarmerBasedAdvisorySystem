"""Schemas for registration, login, tokens, and the account of the logged-in user."""

import enum
from datetime import datetime

from pydantic import BaseModel, Field

from app.model.enums import ConsentType
from app.schema.fields import Email, LanguageCode, Phone
from app.schema.user import USERNAME_PATTERN, UserRead

Password = Field(min_length=8, max_length=128)


class RegisterRequest(BaseModel):  # Self-registration. The new user gets the farmer role.
    username: str = Field(min_length=3, max_length=50, pattern=USERNAME_PATTERN)
    email: Email
    password: str = Password
    phone_number: Phone | None = None
    full_name: str | None = Field(None, max_length=150)
    preferred_language: LanguageCode = "en"
    consents: list[ConsentType] = Field(
        default_factory=list, description="Consents that the user gives on the registration form"
    )


class LoginRequest(BaseModel):
    login: str = Field(min_length=1, max_length=100, description="Username, email, or phone number")
    password: str = Field(min_length=1, max_length=128)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Seconds until the access token expires")
    refresh_expires_at: datetime


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1, max_length=200)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Password


class PasswordResetRequest(BaseModel):
    login: str = Field(min_length=1, max_length=100, description="Username, email, or phone number")


class PasswordResetConfirm(BaseModel):
    token: str = Field(min_length=1, max_length=200)
    new_password: str = Password


class VerificationChannel(str, enum.Enum):
    EMAIL = "email"
    PHONE = "phone"


class VerificationRequest(BaseModel):
    channel: VerificationChannel


class VerificationConfirm(BaseModel):
    channel: VerificationChannel
    code: str = Field(min_length=1, max_length=200, description="Code from the SMS, or token from the email")


class MeRead(UserRead):  # The account of the logged-in user, with what the user can do
    privileges: list[str]
    modules: list[str]


class MeUpdate(BaseModel):  # Fields that users can change on their own account
    email: Email | None = None
    phone_number: Phone | None = None
    full_name: str | None = Field(None, max_length=150)
    preferred_language: LanguageCode | None = None


class Accepted(BaseModel):
    detail: str
