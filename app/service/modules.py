"""Business rules for modules."""

from app.model.modules import Module
from app.repository.modules import ModuleRepository
from app.service.base import BaseService
from app.service.role import RBAC_PERMISSIONS


class ModuleService(BaseService[Module]):
    repository_class = ModuleRepository
    label = "Module"
    permissions = RBAC_PERMISSIONS

    def check_delete(self, item):
        if item.privileges:  # A delete would also delete the privileges that roles use
            return f"Module '{item.name}' has privileges. Delete its privileges first."
        return None
