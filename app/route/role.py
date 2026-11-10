"""Routes for roles."""

from app.controller.role import RoleController
from app.route.factory import build_crud_router

router = build_crud_router(RoleController, prefix="/roles", tag="Roles")
