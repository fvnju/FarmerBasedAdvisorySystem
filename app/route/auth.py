"""Routes for authentication and the account of the logged-in user."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.controller.auth import AuthController
from app.database import get_db
from app.route.dependencies import CurrentActor
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

router = APIRouter(prefix="/auth", tags=["Authentication"])
Db = Annotated[Session, Depends(get_db)]


def public(db: Db) -> AuthController:  # Routes that work without a login
    return AuthController(db)


def private(actor: CurrentActor, db: Db) -> AuthController:  # Routes that need a login
    return AuthController(db, actor)


Public = Annotated[AuthController, Depends(public)]
Private = Annotated[AuthController, Depends(private)]
NO_CONTENT = {"status_code": status.HTTP_204_NO_CONTENT, "response_class": Response}


@router.post("/register", response_model=MeRead, status_code=status.HTTP_201_CREATED, summary="Register as a farmer")
def register(payload: RegisterRequest, controller: Public):
    return controller.register(payload)


@router.post("/login", response_model=TokenPair, summary="Log in with username, email, or phone number")
def login(payload: LoginRequest, controller: Public):
    return controller.login(payload)


@router.post("/refresh", response_model=TokenPair, summary="Get new tokens. The old refresh token stops working.")
def refresh(payload: RefreshRequest, controller: Public):
    return controller.refresh(payload)


@router.post("/logout", summary="Stop the session of this refresh token", **NO_CONTENT)
def logout(payload: RefreshRequest, controller: Public):
    controller.logout(payload)


@router.post("/logout-all", summary="Stop all sessions of the logged-in user", **NO_CONTENT)
def logout_all(controller: Private):
    controller.logout_all()


@router.get("/me", response_model=MeRead, summary="Get the account, privileges, and modules of the logged-in user")
def me(controller: Private):
    return controller.me()


@router.patch("/me", response_model=MeRead, summary="Update the account of the logged-in user")
def update_me(payload: MeUpdate, controller: Private):
    return controller.update_me(payload)


@router.post("/change-password", response_model=TokenPair, summary="Change the password. Other sessions stop.")
def change_password(payload: ChangePasswordRequest, controller: Private):
    return controller.change_password(payload)


@router.post(
    "/password-reset/request",
    response_model=Accepted,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Send a password-reset token",
)
def request_password_reset(payload: PasswordResetRequest, controller: Public):
    return controller.request_password_reset(payload)


@router.post("/password-reset/confirm", summary="Set a new password with the reset token", **NO_CONTENT)
def confirm_password_reset(payload: PasswordResetConfirm, controller: Public):
    controller.confirm_password_reset(payload)


@router.post(
    "/verification/request",
    response_model=Accepted,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Send a verification code to the email or the phone",
)
def request_verification(payload: VerificationRequest, controller: Private):
    return controller.request_verification(payload)


@router.post("/verification/confirm", response_model=MeRead, summary="Verify the email or the phone with the code")
def confirm_verification(payload: VerificationConfirm, controller: Private):
    return controller.confirm_verification(payload)
