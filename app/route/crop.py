"""Routes for crops."""

from app.controller.crop import CropController
from app.route.factory import build_crud_router

router = build_crud_router(CropController, prefix="/crops", tag="Crops")
