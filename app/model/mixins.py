from sqlalchemy import Column, DateTime, func  # Import column tools


class TimestampMixin:  # Add created_at and updated_at to a model
    created_at = Column(
        DateTime, nullable=False, server_default=func.now()
    )  # Set by the database on insert
    updated_at = Column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )  # Changed on each update
