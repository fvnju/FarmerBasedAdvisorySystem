"""Controllers for advisory requests, advisory responses, advisory explanations, advisory citations."""

from app.controller.base import BaseController
from app.schema.advisory import (
    AdvisoryCitationCreate,
    AdvisoryCitationQuery,
    AdvisoryCitationRead,
    AdvisoryCitationUpdate,
    AdvisoryExplanationCreate,
    AdvisoryExplanationQuery,
    AdvisoryExplanationRead,
    AdvisoryExplanationUpdate,
    AdvisoryRequestCreate,
    AdvisoryRequestQuery,
    AdvisoryRequestRead,
    AdvisoryRequestUpdate,
    AdvisoryResponseCreate,
    AdvisoryResponseQuery,
    AdvisoryResponseRead,
    AdvisoryResponseUpdate,
)
from app.service.advisory import (
    AdvisoryCitationService,
    AdvisoryExplanationService,
    AdvisoryRequestService,
    AdvisoryResponseService,
)


class AdvisoryRequestController(BaseController):
    service_class = AdvisoryRequestService
    read_schema = AdvisoryRequestRead
    create_schema = AdvisoryRequestCreate
    update_schema = AdvisoryRequestUpdate
    query_schema = AdvisoryRequestQuery


class AdvisoryResponseController(BaseController):
    service_class = AdvisoryResponseService
    read_schema = AdvisoryResponseRead
    create_schema = AdvisoryResponseCreate
    update_schema = AdvisoryResponseUpdate
    query_schema = AdvisoryResponseQuery


class AdvisoryExplanationController(BaseController):
    service_class = AdvisoryExplanationService
    read_schema = AdvisoryExplanationRead
    create_schema = AdvisoryExplanationCreate
    update_schema = AdvisoryExplanationUpdate
    query_schema = AdvisoryExplanationQuery


class AdvisoryCitationController(BaseController):
    service_class = AdvisoryCitationService
    read_schema = AdvisoryCitationRead
    create_schema = AdvisoryCitationCreate
    update_schema = AdvisoryCitationUpdate
    query_schema = AdvisoryCitationQuery
