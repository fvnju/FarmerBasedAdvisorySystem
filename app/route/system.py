"""Routes for system operations: root, health check, and seed data."""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.controller.system import SystemController
from app.database import get_db
from app.route.dependencies import OptionalActor

router = APIRouter(tags=["System"])
Db = Annotated[Session, Depends(get_db)]


@router.get("/", summary="Show that the API is running")
def read_root():
    return {"message": "Smart Farmer Advisory System is running!"}


@router.get("/health", summary="Check the API and the database")
def health(db: Db):
    ok, body = SystemController(db).health()
    return JSONResponse(status_code=200 if ok else 503, content=body)


@router.post(
    "/seed-data",
    summary="Make roles, privileges, and the first admin",
    description="Open while no user exists. After that, it needs the privilege rbac.manage.",
)
def seed_data(db: Db, actor: OptionalActor):
    return SystemController(db, actor).seed()
