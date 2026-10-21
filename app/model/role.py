from sqlalchemy import Column, Integer, String  # Import column types
from sqlalchemy.orm import relationship  # Import relationship
from app.database import Base  # Import Base


class Role(Base):  # Define Role model
    __tablename__ = "roles"  # Table name

    id = Column(Integer, primary_key=True, index=True)  # ID field
    name = Column(String(50), unique=True, index=True, nullable=False)  # Name field

    users = relationship(
        "User", secondary="user_role", back_populates="roles"
    )  # Reverse relationship
