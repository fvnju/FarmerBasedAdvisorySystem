from sqlalchemy import Column, Integer, String  # Import column types
from sqlalchemy.orm import relationship  # Import relationship
from app.database import Base  # Import Base


class Module(Base):  # A feature area of the app, for example "farms" or "knowledge"
    __tablename__ = "modules"  # Table name

    id = Column(Integer, primary_key=True, index=True)  # ID field
    name = Column(String(50), unique=True, index=True, nullable=False)  # Code name
    description = Column(String(255), nullable=True)  # What the module contains

    roles = relationship(
        "Role", secondary="role_modules", back_populates="modules"
    )  # Roles that can open this module
    privileges = relationship(
        "Privilege", back_populates="module", cascade="all, delete-orphan"
    )  # Actions inside this module
