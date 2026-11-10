"""Controllers for roles."""

from app.controller.base import BaseController
from app.schema.role import (
    RoleCreate,
    RoleQuery,
    RoleRead,
    RoleUpdate,
)
from app.service.role import RoleService


class RoleController(BaseController):
    service_class = RoleService
    read_schema = RoleRead
    create_schema = RoleCreate
    update_schema = RoleUpdate
    query_schema = RoleQuery
