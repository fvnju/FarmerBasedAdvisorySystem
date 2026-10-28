from sqlalchemy import (
    Table,
    Column,
    Integer,
    ForeignKey,
)  # Import table and column tools
from app.database import Base  # Import Base

role_privileges_association = Table(  # Define the association table
    "role_privileges",  # Table name in database
    Base.metadata,  # Attach to Base metadata
    Column(
        "role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    ),  # Role foreign key
    Column(
        "privilege_id",
        Integer,
        ForeignKey("privileges.id", ondelete="CASCADE"),
        primary_key=True,
    ),  # Privilege foreign key
)
