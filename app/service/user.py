"""Business rules for users."""

from app.core.exceptions import ConflictError, InvalidInputError
from app.core.security import hash_password
from app.model.user import User
from app.repository.agent_assignment import AgentFarmerAssignmentRepository
from app.repository.role import RoleRepository
from app.repository.user import UserRepository
from app.service.base import BaseService
from app.service.role import require_role

ADMIN_ROLE = "admin"
FARMER_ROLE = "farmer"


class UserService(BaseService[User]):
    repository_class = UserRepository
    label = "User"
    module = "users"

    def prepare(self, data, current):
        is_self = current is not None and self.actor is not None and current.id == self.actor.id
        if is_self and data.get("is_active") is False:
            raise InvalidInputError("You cannot deactivate your own account.")
        if "password" in data:  # Keep only the hash
            password = data.pop("password")
            if not password:
                raise InvalidInputError("The password must not be empty.", {"fields": ["password"]})
            data["hashed_password"] = hash_password(password)
        if data.get("email"):
            data["email"] = data["email"].strip().lower()  # One account for each address, in any letter case
            if current is not None and data["email"] != current.email:
                data["email_verified_at"] = None  # A new address must be verified again
        if "phone_number" in data and current is not None and data["phone_number"] != current.phone_number:
            data["phone_verified_at"] = None
        if "role_ids" in data:  # null or [] removes all roles
            self._require_privilege("users.assign_roles")
            data["roles"] = self._load_many(RoleRepository(self.db), data.pop("role_ids"), "role")
        elif current is None and self.is_scoped:
            data["roles"] = [require_role(self.db, FARMER_ROLE)]  # Assisted registration
        if current is not None and "roles" in data:
            self._protect_last_admin(current, keeps_admin=any(r.name == ADMIN_ROLE for r in data["roles"]))
        if current is not None and data.get("is_active") is False:
            self._protect_last_admin(current, keeps_admin=False)
        return data

    def after_save(self, item, created):
        if created and self.is_scoped:  # An agent registered a farmer, so the agent helps that farmer
            AgentFarmerAssignmentRepository(self.db).create({"agent_id": self.actor.id, "farmer_id": item.id})

    def check_delete(self, item):
        if self.actor is not None and item.id == self.actor.id:
            return "You cannot delete your own account."
        if self._is_last_admin(item):
            return "This is the last active admin. Give the admin role to another user first."
        return None

    def _is_last_admin(self, user) -> bool:
        is_admin = user.is_active and any(role.name == ADMIN_ROLE for role in user.roles)
        return is_admin and self.repo.count_active_with_role(ADMIN_ROLE) <= 1

    def _protect_last_admin(self, user, keeps_admin: bool) -> None:
        if not keeps_admin and self._is_last_admin(user):
            raise ConflictError("This is the last active admin. Give the admin role to another user first.")
