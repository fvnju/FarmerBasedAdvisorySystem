"""Database queries for roles."""

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.model.role import Role
from app.repository.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    model = Role
    search_fields = (Role.name, Role.description)
    sort_fields = ("id", "name")
    load_options = (selectinload(Role.modules), selectinload(Role.privileges))

    def get_by_name(self, name: str) -> Role | None:
        return self.db.scalar(select(Role).where(Role.name == name))
