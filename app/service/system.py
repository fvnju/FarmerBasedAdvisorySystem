"""Business rules for system operations: health check and seed data."""

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.actor import Actor
from app.core.exceptions import ConflictError, ForbiddenError, UnauthorizedError
from app.repository.role import RoleRepository
from app.repository.system import SystemRepository
from app.repository.user import UserRepository
from app.seed import SEED_ADMIN_USERNAME, seed_rbac, seed_test_user
from app.service.base import transaction
from app.service.user import ADMIN_ROLE

SEED_PRIVILEGE = "rbac.manage"


class SystemService:
    def __init__(self, db: Session, actor: Actor | None = None):
        self.db = db
        self.actor = actor

    def database_ok(self) -> bool:
        try:
            return SystemRepository(self.db).ping()
        except SQLAlchemyError:
            return False

    def ensure_rbac(self) -> bool:
        """Make the roles and privileges if no role exists. Return True if it made them.

        The app calls it at start-up, so registration always finds the farmer role.
        It does not change roles that exist, and it does not make the admin user.
        """
        if RoleRepository(self.db).count() > 0:
            return False
        with transaction(self.db):
            seed_rbac(self.db)
        return True

    def seed(self) -> None:
        """Make the RBAC data and the first admin.

        With no active admin, anyone can call it, so a new installation can start.
        Farmers can register before the first admin exists, so the check is for an admin, not for any user.
        After that, only a user with rbac.manage can call it, for example to add new privileges.
        """
        users = UserRepository(self.db)
        if users.count_active_with_role(ADMIN_ROLE) > 0:
            if self.actor is None:
                raise UnauthorizedError("Log in as an administrator to run the seed again.")
            if not self.actor.has(SEED_PRIVILEGE):
                raise ForbiddenError(f"You need the privilege '{SEED_PRIVILEGE}'.")
        existing = users.get_by_login(SEED_ADMIN_USERNAME)
        if existing is not None and not any(role.name == ADMIN_ROLE for role in existing.roles):
            raise ConflictError(
                f"A user with the name '{SEED_ADMIN_USERNAME}' exists and is not an admin. "
                "Give that user the admin role in the database, or delete that user."
            )
        with transaction(self.db):
            seed_rbac(self.db)
            self.db.flush()  # Write the roles before the user looks them up
            seed_test_user(self.db)
