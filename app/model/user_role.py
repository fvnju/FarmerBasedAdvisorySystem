from sqlalchemy import (
    Table,
    Column,
    Integer,
    ForeignKey,
)  # Import table and column tools
from app.database import Base  # Import Base

user_role_association = Table(  # Define the association table
    "user_role",  # Table name in database
    Base.metadata,  # Attach to Base metadata
    Column(
        "user_id", Integer, ForeignKey("users.id"), primary_key=True
    ),  # User foreign key
    Column(
        "role_id", Integer, ForeignKey("roles.id"), primary_key=True
    ),  # Role foreign key
)
