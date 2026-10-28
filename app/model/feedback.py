from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)  # Import column types
from sqlalchemy.orm import relationship  # Import relationship
from app.database import Base  # Import Base
from app.model.enums import FeedbackOutcome, db_enum  # Import enums


class AdvisoryFeedback(Base):  # What the farmer did with one piece of advice
    __tablename__ = "advisory_feedback"  # Table name

    id = Column(Integer, primary_key=True, index=True)  # ID field
    response_id = Column(
        Integer,
        ForeignKey("advisory_responses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )  # Advice the feedback is about
    outcome = Column(db_enum(FeedbackOutcome), nullable=False)  # Followed, modified, or rejected
    reason = Column(Text, nullable=True)  # Why the farmer changed or rejected the action
    action_date = Column(Date, nullable=True)  # Date the farmer did the action
    recorded_by_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )  # Farmer or agent who entered it
    client_reference = Column(
        String(36), unique=True, nullable=True
    )  # UUID from the offline client, to stop duplicate syncs
    created_at = Column(DateTime, nullable=False, server_default=func.now())  # Entry time

    response = relationship("AdvisoryResponse", back_populates="feedback")  # Advice
    recorded_by = relationship("User")  # User who entered it


class FieldObservation(Base):  # A later observation on the field. Reported values stay separate from verified ones.
    __tablename__ = "field_observations"  # Table name

    id = Column(Integer, primary_key=True, index=True)  # ID field
    crop_cycle_id = Column(
        Integer, ForeignKey("crop_cycles.id", ondelete="CASCADE"), nullable=False, index=True
    )  # Season of the observation
    feedback_id = Column(
        Integer, ForeignKey("advisory_feedback.id", ondelete="SET NULL"), nullable=True
    )  # Feedback the observation follows, if any
    observed_on = Column(Date, nullable=False)  # Date of the observation
    observation = Column(Text, nullable=False)  # What the farmer or agent saw
    is_verified = Column(
        Boolean, nullable=False, server_default="0"
    )  # True only for a measured or checked value
    verified_by_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )  # Specialist who verified it
    recorded_by_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )  # User who entered it
    client_reference = Column(
        String(36), unique=True, nullable=True
    )  # UUID from the offline client, to stop duplicate syncs
    created_at = Column(DateTime, nullable=False, server_default=func.now())  # Entry time

    crop_cycle = relationship("CropCycle", back_populates="observations")  # Season
    feedback = relationship("AdvisoryFeedback")  # Linked feedback
    verified_by = relationship("User", foreign_keys=[verified_by_id])  # Verifier
    recorded_by = relationship("User", foreign_keys=[recorded_by_id])  # Entry user
