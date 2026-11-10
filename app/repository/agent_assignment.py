"""Database queries for the links between extension agents and farmers."""

from sqlalchemy import or_

from app.model.agent_assignment import AgentFarmerAssignment
from app.model.user import User
from app.repository.base import LIKE_ESCAPE, BaseRepository
from app.repository.scope import OwnerScope


class AgentFarmerAssignmentRepository(BaseRepository[AgentFarmerAssignment]):
    model = AgentFarmerAssignment
    sort_fields = ("id", "assigned_at", "ended_at")

    def owner_condition(self, scope: OwnerScope):  # Links where the user is the agent or the farmer
        return or_(
            scope.is_self(AgentFarmerAssignment.agent_id),
            scope.is_self(AgentFarmerAssignment.farmer_id),
        )

    def search_condition(self, pattern):  # Username or full name of the agent or the farmer
        def matches(relationship):
            return relationship.has(
                or_(
                    User.username.ilike(pattern, escape=LIKE_ESCAPE),
                    User.full_name.ilike(pattern, escape=LIKE_ESCAPE),
                )
            )

        return or_(matches(AgentFarmerAssignment.agent), matches(AgentFarmerAssignment.farmer))

    def filter_condition(self, name, value):
        if name == "active":
            column = AgentFarmerAssignment.ended_at
            return column.is_(None) if value else column.is_not(None)
        return super().filter_condition(name, value)
