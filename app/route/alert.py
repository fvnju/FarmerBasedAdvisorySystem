"""Routes for alerts."""

from app.controller.alert import AlertController
from app.route.factory import build_crud_router

router = build_crud_router(AlertController, prefix="/alerts", tag="Alerts")
