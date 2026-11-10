"""Database queries for system checks."""

from sqlalchemy import select
from sqlalchemy.orm import Session


class SystemRepository:
    def __init__(self, db: Session):
        self.db = db

    def ping(self) -> bool:  # True if the database answers
        return self.db.scalar(select(1)) == 1
