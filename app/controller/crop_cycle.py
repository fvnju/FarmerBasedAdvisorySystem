"""Controllers for crop cycles."""

from app.controller.base import BaseController
from app.schema.crop_cycle import (
    CropCycleCreate,
    CropCycleQuery,
    CropCycleRead,
    CropCycleUpdate,
)
from app.service.crop_cycle import CropCycleService


class CropCycleController(BaseController):
    service_class = CropCycleService
    read_schema = CropCycleRead
    create_schema = CropCycleCreate
    update_schema = CropCycleUpdate
    query_schema = CropCycleQuery
