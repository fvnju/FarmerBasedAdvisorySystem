"""Routes for users."""

from app.controller.user import UserController
from app.route.factory import build_crud_router

router = build_crud_router(UserController, prefix="/users", tag="Users")
