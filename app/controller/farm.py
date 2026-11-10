"""Controllers for farms, farm resources, soil records."""

from app.controller.base import BaseController
from app.schema.farm import (
    FarmCreate,
    FarmQuery,
    FarmRead,
    FarmResourceCreate,
    FarmResourceQuery,
    FarmResourceRead,
    FarmResourceUpdate,
    FarmUpdate,
    SoilRecordCreate,
    SoilRecordQuery,
    SoilRecordRead,
    SoilRecordUpdate,
)
from app.service.farm import (
    FarmResourceService,
    FarmService,
    SoilRecordService,
)


class FarmController(BaseController):
    service_class = FarmService
    read_schema = FarmRead
    create_schema = FarmCreate
    update_schema = FarmUpdate
    query_schema = FarmQuery


class FarmResourceController(BaseController):
    service_class = FarmResourceService
    read_schema = FarmResourceRead
    create_schema = FarmResourceCreate
    update_schema = FarmResourceUpdate
    query_schema = FarmResourceQuery


class SoilRecordController(BaseController):
    service_class = SoilRecordService
    read_schema = SoilRecordRead
    create_schema = SoilRecordCreate
    update_schema = SoilRecordUpdate
    query_schema = SoilRecordQuery
