"""Routes for advisory feedback, field observations."""

from app.controller.feedback import (
    AdvisoryFeedbackController,
    FieldObservationController,
)
from app.route.factory import build_crud_router

routers = [
    build_crud_router(AdvisoryFeedbackController, prefix="/advisory-feedback", tag="Advisory feedback"),
    build_crud_router(FieldObservationController, prefix="/field-observations", tag="Field observations"),
]
