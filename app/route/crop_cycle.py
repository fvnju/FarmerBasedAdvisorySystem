"""Routes for crop cycles."""

from app.controller.crop_cycle import CropCycleController
from app.route.factory import build_crud_router

router = build_crud_router(CropCycleController, prefix="/crop-cycles", tag="Crop cycles")
