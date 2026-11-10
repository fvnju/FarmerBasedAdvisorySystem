"""Routes for consent records."""

from app.controller.consent import ConsentRecordController
from app.route.factory import build_crud_router

router = build_crud_router(ConsentRecordController, prefix="/consent-records", tag="Consent records")
