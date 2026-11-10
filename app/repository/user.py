"""Database queries for users."""

from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from app.model.role import Role
from app.model.user import User
from app.repository.base import BaseRepository
from app.repository.scope import OwnerScope


class UserRepository(BaseRepository[User]):
    model = User
    search_fields = (User.username, User.email, User.full_name, User.phone_number)
    sort_fields = ("id", "username", "email", "full_name", "created_at", "updated_at", "last_login_at")
    load_options = (selectinload(User.roles),)  # One more query for each page, not one for each user

    def owner_condition(self, scope: OwnerScope):
        return scope.matches(User.id)  # The user and the farmers assigned to the user

    def filter_condition(self, name, value):
        if name == "role_id":
            return User.roles.any(Role.id == value)
        return super().filter_condition(name, value)

    def get_by_login(self, login: str) -> User | None:  # Find by username, email, or phone number
        login = login.strip()
        stmt = select(User).where(
            or_(User.username == login, func.lower(User.email) == login.lower(), User.phone_number == login)
        )
        return self.db.scalar(stmt)

    def get_with_privileges(self, user_id: int) -> User | None:  # Roles and privileges in two more queries
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.roles).selectinload(Role.privileges))
        )
        return self.db.scalar(stmt)

    def count_active_with_role(self, role_name: str) -> int:
        stmt = select(func.count(User.id)).where(
            User.is_active.is_(True), User.roles.any(Role.name == role_name)
        )
        return self.db.scalar(stmt) or 0

    def any_exists(self) -> bool:
        return self.db.scalar(select(User.id).limit(1)) is not None
