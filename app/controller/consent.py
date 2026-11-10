"""Controllers for consent records."""

from app.controller.base import BaseController
from app.schema.consent import (
    ConsentRecordCreate,
    ConsentRecordQuery,
    ConsentRecordRead,
)
from app.service.consent import ConsentRecordService


class ConsentRecordController(BaseController):
    service_class = ConsentRecordService
    read_schema = ConsentRecordRead
    create_schema = ConsentRecordCreate
    query_schema = ConsentRecordQuery
