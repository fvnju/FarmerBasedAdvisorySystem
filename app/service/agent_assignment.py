"""Business rules for the links between extension agents and farmers."""

from app.core.exceptions import InvalidInputError
from app.model.agent_assignment import AgentFarmerAssignment
from app.repository.agent_assignment import AgentFarmerAssignmentRepository
from app.schema.common import Operation
from app.service.base import BaseService


class AgentFarmerAssignmentService(BaseService[AgentFarmerAssignment]):
    repository_class = AgentFarmerAssignmentRepository
    label = "Agent assignment"
    module = "assignments"
    permissions = {
        Operation.CREATE: "assignments.manage",
        Operation.UPDATE: "assignments.manage",
        Operation.DELETE: "assignments.manage",
    }

    def validate(self, values, current):
        if values["agent_id"] == values["farmer_id"]:
            raise InvalidInputError("A user cannot be the agent of their own account.")
        assigned_at, ended_at = values["assigned_at"], values["ended_at"]
        if assigned_at is not None and ended_at is not None and ended_at < assigned_at:
            raise InvalidInputError("ended_at must not be before assigned_at.", {"fields": ["ended_at"]})
