"""Controllers for advisory feedback, field observations."""

from app.controller.base import BaseController
from app.schema.feedback import (
    AdvisoryFeedbackCreate,
    AdvisoryFeedbackQuery,
    AdvisoryFeedbackRead,
    AdvisoryFeedbackUpdate,
    FieldObservationCreate,
    FieldObservationQuery,
    FieldObservationRead,
    FieldObservationUpdate,
)
from app.service.feedback import (
    AdvisoryFeedbackService,
    FieldObservationService,
)


class AdvisoryFeedbackController(BaseController):
    service_class = AdvisoryFeedbackService
    read_schema = AdvisoryFeedbackRead
    create_schema = AdvisoryFeedbackCreate
    update_schema = AdvisoryFeedbackUpdate
    query_schema = AdvisoryFeedbackQuery


class FieldObservationController(BaseController):
    service_class = FieldObservationService
    read_schema = FieldObservationRead
    create_schema = FieldObservationCreate
    update_schema = FieldObservationUpdate
    query_schema = FieldObservationQuery
