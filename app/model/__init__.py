from app.model.user import User  # Import User model
from app.model.role import Role  # Import Role model
from app.model.user_role import user_role_association  # Import association table

__all__ = ["User", "Role", "user_role_association"]  # Expose them for easy importing
