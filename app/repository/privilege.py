"""Database queries for privileges."""

from app.model.privilege import Privilege
from app.repository.base import BaseRepository


class PrivilegeRepository(BaseRepository[Privilege]):
    model = Privilege
    search_fields = (Privilege.code, Privilege.description)
    sort_fields = ("id", "code", "module_id")
