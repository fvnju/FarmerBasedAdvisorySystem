"""Controllers for users."""

from app.controller.base import BaseController
from app.schema.user import (
    UserCreate,
    UserQuery,
    UserRead,
    UserUpdate,
)
from app.service.user import UserService


class UserController(BaseController):
    service_class = UserService
    read_schema = UserRead
    create_schema = UserCreate
    update_schema = UserUpdate
    query_schema = UserQuery
