"""Data scope for users who do not have the privilege data.all_farmers.

Such a user sees their own records and the records of the farmers assigned to them.
The assignment list is a subquery, so a new assignment in the same transaction is included at once.
"""

from dataclasses import dataclass

from sqlalchemy import ColumnElement, Select, or_, select

from app.model.agent_assignment import AgentFarmerAssignment


@dataclass(frozen=True)
class OwnerScope:
    user_id: int  # The logged-in user

    def assigned_farmer_ids(self) -> Select:  # Farmers that this user helps now
        return select(AgentFarmerAssignment.farmer_id).where(
            AgentFarmerAssignment.agent_id == self.user_id,
            AgentFarmerAssignment.ended_at.is_(None),
        )

    def matches(self, user_column) -> ColumnElement:  # The column is the user or an assigned farmer
        return or_(user_column == self.user_id, user_column.in_(self.assigned_farmer_ids()))

    def is_self(self, user_column) -> ColumnElement:  # The column is the user only
        return user_column == self.user_id
