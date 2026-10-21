from sqlalchemy import Column, Integer, String  # Import column types
from sqlalchemy.orm import relationship  # Import relationship
from app.database import Base  # Import Base


class User(Base):  # Define User model
    __tablename__ = "users"  # Table name

    id = Column(Integer, primary_key=True, index=True)  # ID field
    username = Column(
        String(50), unique=True, index=True, nullable=False
    )  # Username field
    email = Column(String(100), unique=True, index=True, nullable=False)  # Email field
    password = Column(String(255), nullable=False)  # Password field

    roles = relationship(
        "Role", secondary="user_role", back_populates="users"
    )  # Many-to-many relationship
