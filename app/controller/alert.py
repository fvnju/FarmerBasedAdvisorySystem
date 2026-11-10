"""Controllers for alerts."""

from app.controller.base import BaseController
from app.schema.alert import (
    AlertCreate,
    AlertQuery,
    AlertRead,
    AlertUpdate,
)
from app.service.alert import AlertService


class AlertController(BaseController):
    service_class = AlertService
    read_schema = AlertRead
    create_schema = AlertCreate
    update_schema = AlertUpdate
    query_schema = AlertQuery
