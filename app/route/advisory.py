"""Routes for advisory requests, advisory responses, advisory explanations, advisory citations."""

from app.controller.advisory import (
    AdvisoryCitationController,
    AdvisoryExplanationController,
    AdvisoryRequestController,
    AdvisoryResponseController,
)
from app.route.factory import build_crud_router

routers = [
    build_crud_router(AdvisoryRequestController, prefix="/advisory-requests", tag="Advisory requests"),
    build_crud_router(AdvisoryResponseController, prefix="/advisory-responses", tag="Advisory responses"),
    build_crud_router(AdvisoryExplanationController, prefix="/advisory-explanations", tag="Advisory explanations"),
    build_crud_router(AdvisoryCitationController, prefix="/advisory-citations", tag="Advisory citations"),
]
