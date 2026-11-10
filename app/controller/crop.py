"""Controllers for crops."""

from app.controller.base import BaseController
from app.schema.crop import (
    CropCreate,
    CropQuery,
    CropRead,
    CropUpdate,
)
from app.service.crop import CropService


class CropController(BaseController):
    service_class = CropService
    read_schema = CropRead
    create_schema = CropCreate
    update_schema = CropUpdate
    query_schema = CropQuery
