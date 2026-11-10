"""Controllers for agent assignments."""

from app.controller.base import BaseController
from app.schema.agent_assignment import (
    AgentFarmerAssignmentCreate,
    AgentFarmerAssignmentQuery,
    AgentFarmerAssignmentRead,
    AgentFarmerAssignmentUpdate,
)
from app.service.agent_assignment import AgentFarmerAssignmentService


class AgentFarmerAssignmentController(BaseController):
    service_class = AgentFarmerAssignmentService
    read_schema = AgentFarmerAssignmentRead
    create_schema = AgentFarmerAssignmentCreate
    update_schema = AgentFarmerAssignmentUpdate
    query_schema = AgentFarmerAssignmentQuery
