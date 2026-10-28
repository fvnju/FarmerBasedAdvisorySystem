from sqlalchemy import Boolean, Column, Integer, String  # Import column types
from sqlalchemy.orm import relationship  # Import relationship
from app.database import Base  # Import Base


class Role(Base):  # Define Role model
    __tablename__ = "roles"  # Table name

    id = Column(Integer, primary_key=True, index=True)  # ID field
    name = Column(String(50), unique=True, index=True, nullable=False)  # Name field
    description = Column(String(255), nullable=True)  # What the role is for
    is_system = Column(
        Boolean, nullable=False, server_default="0"
    )  # True for built-in roles that must not be deleted

    users = relationship(
        "User", secondary="user_role", back_populates="roles"
    )  # Reverse relationship
    modules = relationship(
        "Module", secondary="role_modules", back_populates="roles"
    )  # Modules this role can open
    privileges = relationship(
        "Privilege", secondary="role_privileges", back_populates="roles"
    )  # Actions this role can do
