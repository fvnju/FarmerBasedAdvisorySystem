"""Business rules for privileges."""

from app.core.exceptions import InvalidInputError
from app.model.privilege import Privilege
from app.repository.modules import ModuleRepository
from app.repository.privilege import PrivilegeRepository
from app.service.base import BaseService
from app.service.role import RBAC_PERMISSIONS


class PrivilegeService(BaseService[Privilege]):
    repository_class = PrivilegeRepository
    label = "Privilege"
    permissions = RBAC_PERMISSIONS

    def validate(self, values, current):
        if not (values.changed("module_id") or values.changed("code")):
            return
        module = self._get_linked(ModuleRepository(self.db), values["module_id"], "Module")
        if not values["code"].startswith(f"{module.name}."):
            raise InvalidInputError(
                f"The code must start with '{module.name}.'.", {"fields": ["code", "module_id"]}
            )
