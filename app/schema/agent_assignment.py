"""Schemas for the links between extension agents and farmers."""

from datetime import datetime

from pydantic import BaseModel

from app.schema.common import ListQuery, ReadSchema
from app.schema.fields import Id


class AgentFarmerAssignmentCreate(BaseModel):
    agent_id: Id
    farmer_id: Id


class AgentFarmerAssignmentUpdate(BaseModel):
    ended_at: datetime | None = None  # Set to stop the access. Set to null to give the access again.


class AgentFarmerAssignmentRead(ReadSchema):
    id: int
    agent_id: int
    farmer_id: int
    assigned_at: datetime
    ended_at: datetime | None


class AgentFarmerAssignmentQuery(ListQuery):
    agent_id: int | None = None
    farmer_id: int | None = None
    active: bool | None = None  # True: ended_at is empty
