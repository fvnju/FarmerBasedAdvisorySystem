"""FastAPI dependencies for authentication. They give the logged-in user to the routes."""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.audit import set_audit_user
from app.core.actor import Actor
from app.core.exceptions import UnauthorizedError
from app.database import get_db
from app.service.auth import AuthService

bearer = HTTPBearer(auto_error=False, description="Access token from POST /api/v1/auth/login")
Credentials = Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]
Db = Annotated[Session, Depends(get_db)]


def get_optional_actor(credentials: Credentials, db: Db) -> Actor | None:  # None if no token is sent
    if credentials is None:
        return None
    actor = AuthService(db).actor_from_access_token(credentials.credentials)
    set_audit_user(actor.id)  # The audit trail records who made each change
    return actor


def get_actor(actor: Annotated[Actor | None, Depends(get_optional_actor)]) -> Actor:  # Login is necessary
    if actor is None:
        raise UnauthorizedError("Log in first. Send the access token as 'Authorization: Bearer <token>'.")
    return actor


CurrentActor = Annotated[Actor, Depends(get_actor)]
OptionalActor = Annotated[Actor | None, Depends(get_optional_actor)]
