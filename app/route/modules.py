"""Routes for modules."""

from app.controller.modules import ModuleController
from app.route.factory import build_crud_router

router = build_crud_router(ModuleController, prefix="/modules", tag="Modules")
