"""Controllers for regions."""

from app.controller.base import BaseController
from app.schema.region import (
    RegionCreate,
    RegionQuery,
    RegionRead,
    RegionUpdate,
)
from app.service.region import RegionService


class RegionController(BaseController):
    service_class = RegionService
    read_schema = RegionRead
    create_schema = RegionCreate
    update_schema = RegionUpdate
    query_schema = RegionQuery
