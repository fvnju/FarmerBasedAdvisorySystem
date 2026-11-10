"""Database queries for modules."""

from app.model.modules import Module
from app.repository.base import BaseRepository


class ModuleRepository(BaseRepository[Module]):
    model = Module
    search_fields = (Module.name, Module.description)
    sort_fields = ("id", "name")
