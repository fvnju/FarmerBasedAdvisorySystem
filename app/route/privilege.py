"""Routes for privileges."""

from app.controller.privilege import PrivilegeController
from app.route.factory import build_crud_router

router = build_crud_router(PrivilegeController, prefix="/privileges", tag="Privileges")
