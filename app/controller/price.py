"""Controllers for price records."""

from app.controller.base import BaseController
from app.schema.price import (
    PriceRecordCreate,
    PriceRecordQuery,
    PriceRecordRead,
    PriceRecordUpdate,
)
from app.service.price import PriceRecordService


class PriceRecordController(BaseController):
    service_class = PriceRecordService
    read_schema = PriceRecordRead
    create_schema = PriceRecordCreate
    update_schema = PriceRecordUpdate
    query_schema = PriceRecordQuery
