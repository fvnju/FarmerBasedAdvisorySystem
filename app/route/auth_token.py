"""Routes for login sessions, one-time tokens."""

from app.controller.auth_token import (
    OneTimeTokenController,
    RefreshTokenController,
)
from app.route.factory import build_crud_router

routers = [
    build_crud_router(RefreshTokenController, prefix="/refresh-tokens", tag="Login sessions"),
    build_crud_router(OneTimeTokenController, prefix="/one-time-tokens", tag="One-time tokens"),
]
