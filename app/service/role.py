"""Business rules for roles."""

from app.core.exceptions import ConflictError
from app.model.role import Role
from app.repository.modules import ModuleRepository
from app.repository.privilege import PrivilegeRepository
from app.repository.role import RoleRepository
from app.schema.common import Operation
from app.service.base import BaseService

RBAC_PERMISSIONS = {
    Operation.LIST: "rbac.read",
    Operation.READ: "rbac.read",
    Operation.CREATE: "rbac.manage",
    Operation.UPDATE: "rbac.manage",
    Operation.DELETE: "rbac.manage",
}


def require_role(db, name: str) -> Role:  # A role that the seed makes. Clear error if the seed has not run.
    role = RoleRepository(db).get_by_name(name)
    if role is None:
        raise ConflictError(f"The role '{name}' does not exist. The roles are not set up yet. Call POST /seed-data first.")
    return role


class RoleService(BaseService[Role]):
    repository_class = RoleRepository
    label = "Role"
    permissions = RBAC_PERMISSIONS

    def prepare(self, data, current):
        if current is not None and current.is_system and "name" in data and data["name"] != current.name:
            raise ConflictError("You cannot rename a system role. The seed data uses its name.")
        if "module_ids" in data:
            data["modules"] = self._load_many(ModuleRepository(self.db), data.pop("module_ids"), "module")
        if "privilege_ids" in data:
            privileges = self._load_many(PrivilegeRepository(self.db), data.pop("privilege_ids"), "privilege")
            data["privileges"] = privileges
            modules = data.get("modules")
            if modules is None:
                modules = list(current.modules) if current is not None else []
            for privilege in privileges:  # A role must open the module of each of its privileges
                if privilege.module not in modules:
                    modules.append(privilege.module)
            data["modules"] = modules
        return data

    def check_delete(self, item):
        if item.is_system:
            return f"Role '{item.name}' is a system role. You cannot delete it."
        return None
