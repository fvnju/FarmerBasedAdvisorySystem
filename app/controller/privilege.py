"""Controllers for privileges."""

from app.controller.base import BaseController
from app.schema.privilege import (
    PrivilegeCreate,
    PrivilegeQuery,
    PrivilegeRead,
    PrivilegeUpdate,
)
from app.service.privilege import PrivilegeService


class PrivilegeController(BaseController):
    service_class = PrivilegeService
    read_schema = PrivilegeRead
    create_schema = PrivilegeCreate
    update_schema = PrivilegeUpdate
    query_schema = PrivilegeQuery
