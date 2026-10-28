from sqlalchemy import Column, ForeignKey, Integer, String  # Import column types
from sqlalchemy.orm import relationship  # Import relationship
from app.database import Base  # Import Base


class Privilege(Base):  # One action in a module, for example "farms.update"
    __tablename__ = "privileges"  # Table name

    id = Column(Integer, primary_key=True, index=True)  # ID field
    module_id = Column(
        Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True
    )  # Module that owns the action
    code = Column(
        String(100), unique=True, index=True, nullable=False
    )  # "<module>.<action>", checked by the API
    description = Column(String(255), nullable=True)  # What the action lets a user do

    module = relationship("Module", back_populates="privileges")  # Parent module
    roles = relationship(
        "Role", secondary="role_privileges", back_populates="privileges"
    )  # Roles that have this privilege
