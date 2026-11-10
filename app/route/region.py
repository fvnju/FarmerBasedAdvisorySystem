"""Routes for regions."""

from app.controller.region import RegionController
from app.route.factory import build_crud_router

router = build_crud_router(RegionController, prefix="/regions", tag="Regions")
