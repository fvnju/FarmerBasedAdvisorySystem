"""Controllers for modules."""

from app.controller.base import BaseController
from app.schema.modules import (
    ModuleCreate,
    ModuleQuery,
    ModuleRead,
    ModuleUpdate,
)
from app.service.modules import ModuleService


class ModuleController(BaseController):
    service_class = ModuleService
    read_schema = ModuleRead
    create_schema = ModuleCreate
    update_schema = ModuleUpdate
    query_schema = ModuleQuery
