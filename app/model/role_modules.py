from sqlalchemy import (
    Table,
    Column,
    Integer,
    ForeignKey,
)  # Import table and column tools
from app.database import Base  # Import Base

role_modules_association = Table(  # Define the association table
    "role_modules",  # Table name in database
    Base.metadata,  # Attach to Base metadata
    Column(
        "role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    ),  # Role foreign key
    Column(
        "module_id",
        Integer,
        ForeignKey("modules.id", ondelete="CASCADE"),
        primary_key=True,
    ),  # Module foreign key
)
