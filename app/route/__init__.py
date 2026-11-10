"""HTTP routes. Each module defines its routers. api_router collects all of them under /api/v1."""

from fastapi import APIRouter

from app.route import auth
from app.route import user
from app.route import role
from app.route import modules
from app.route import privilege
from app.route import auth_token
from app.route import consent
from app.route import agent_assignment
from app.route import audit_log
from app.route import region
from app.route import crop
from app.route import farm
from app.route import crop_cycle
from app.route import knowledge
from app.route import weather
from app.route import price
from app.route import advisory
from app.route import feedback
from app.route import alert

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(user.router)
api_router.include_router(role.router)
api_router.include_router(modules.router)
api_router.include_router(privilege.router)
for router in auth_token.routers:
    api_router.include_router(router)
api_router.include_router(consent.router)
api_router.include_router(agent_assignment.router)
api_router.include_router(audit_log.router)
api_router.include_router(region.router)
api_router.include_router(crop.router)
for router in farm.routers:
    api_router.include_router(router)
api_router.include_router(crop_cycle.router)
for router in knowledge.routers:
    api_router.include_router(router)
for router in weather.routers:
    api_router.include_router(router)
api_router.include_router(price.router)
for router in advisory.routers:
    api_router.include_router(router)
for router in feedback.routers:
    api_router.include_router(router)
api_router.include_router(alert.router)
