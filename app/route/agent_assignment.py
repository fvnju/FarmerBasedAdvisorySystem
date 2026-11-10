"""Routes for agent assignments."""

from app.controller.agent_assignment import AgentFarmerAssignmentController
from app.route.factory import build_crud_router

router = build_crud_router(AgentFarmerAssignmentController, prefix="/agent-assignments", tag="Agent assignments")
