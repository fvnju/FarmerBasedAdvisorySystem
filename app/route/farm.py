"""Routes for farms, farm resources, soil records."""

from app.controller.farm import (
    FarmController,
    FarmResourceController,
    SoilRecordController,
)
from app.route.factory import build_crud_router

routers = [
    build_crud_router(FarmController, prefix="/farms", tag="Farms"),
    build_crud_router(FarmResourceController, prefix="/farm-resources", tag="Farm resources"),
    build_crud_router(SoilRecordController, prefix="/soil-records", tag="Soil records"),
]
