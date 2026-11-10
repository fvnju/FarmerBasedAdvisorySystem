"""Controller for system operations."""

from sqlalchemy.orm import Session

from app.core.actor import Actor
from app.service.system import SystemService


class SystemController:
    def __init__(self, db: Session, actor: Actor | None = None):
        self.service = SystemService(db, actor)

    def health(self) -> tuple[bool, dict]:
        ok = self.service.database_ok()
        return ok, {"status": "ok" if ok else "unavailable", "database": "ok" if ok else "unavailable"}

    def seed(self) -> dict:
        self.service.seed()
        return {"message": "Data seeded successfully!"}
