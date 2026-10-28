from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func  # Import column tools
from sqlalchemy.orm import relationship  # Import relationship
from app.database import Base  # Import Base
from app.model.enums import ConsentType, db_enum  # Import consent types


class ConsentRecord(Base):  # One grant or withdrawal of consent. Rows are never updated.
    __tablename__ = "consent_records"  # Table name

    id = Column(Integer, primary_key=True, index=True)  # ID field
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )  # User who gives or withdraws consent
    consent_type = Column(db_enum(ConsentType), nullable=False)  # What the consent covers
    granted = Column(Boolean, nullable=False)  # True to grant, False to withdraw
    policy_version = Column(String(20), nullable=False)  # Version of the privacy text shown
    recorded_by_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )  # Extension agent who recorded it, if assisted
    created_at = Column(DateTime, nullable=False, server_default=func.now())  # Time of the decision

    user = relationship(
        "User", foreign_keys=[user_id], back_populates="consents"
    )  # User who gives consent
    recorded_by = relationship("User", foreign_keys=[recorded_by_id])  # Assisting agent
