"""Routes for price records."""

from app.controller.price import PriceRecordController
from app.route.factory import build_crud_router

router = build_crud_router(PriceRecordController, prefix="/price-records", tag="Price records")
