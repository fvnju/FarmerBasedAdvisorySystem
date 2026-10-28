from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    UniqueConstraint,
    func,
)  # Import column tools
from sqlalchemy.orm import relationship  # Import relationship
from app.database import Base  # Import Base


class AgentFarmerAssignment(Base):  # Links an extension agent to a farmer that the agent helps
    __tablename__ = "agent_farmer_assignments"  # Table name
    __table_args__ = (
        UniqueConstraint("agent_id", "farmer_id", name="uq_agent_farmer"),
    )  # One row for each pair

    id = Column(Integer, primary_key=True, index=True)  # ID field
    agent_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )  # Extension agent
    farmer_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )  # Farmer
    assigned_at = Column(DateTime, nullable=False, server_default=func.now())  # Start of access
    ended_at = Column(DateTime, nullable=True)  # Set to stop the agent's access

    agent = relationship(
        "User", foreign_keys=[agent_id], back_populates="assigned_farmers"
    )  # Extension agent
    farmer = relationship(
        "User", foreign_keys=[farmer_id], back_populates="assigned_agents"
    )  # Farmer
