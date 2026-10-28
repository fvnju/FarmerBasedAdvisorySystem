from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)  # Import column types
from sqlalchemy.orm import relationship  # Import relationship
from app.database import Base  # Import Base
from app.model.enums import (
    AccessMode,
    AdvisoryActionType,
    AdvisoryStatus,
    Affordability,
    ValidationStatus,
    db_enum,
)  # Import enums
from app.model.mixins import TimestampMixin  # Import created_at and updated_at


class AdvisoryRequest(TimestampMixin, Base):  # A question from a farmer
    __tablename__ = "advisory_requests"  # Table name

    id = Column(Integer, primary_key=True, index=True)  # ID field
    farmer_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )  # Farmer the advice is for
    assisted_by_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )  # Extension agent, if assisted
    access_mode = Column(db_enum(AccessMode), nullable=False)  # Independent or assisted
    farm_id = Column(
        Integer, ForeignKey("farms.id", ondelete="SET NULL"), nullable=True, index=True
    )  # Farm the question is about
    crop_cycle_id = Column(
        Integer, ForeignKey("crop_cycles.id", ondelete="SET NULL"), nullable=True, index=True
    )  # Season the question is about
    action_type = Column(db_enum(AdvisoryActionType), nullable=False)  # Kind of action asked about
    question = Column(Text, nullable=False)  # Text the farmer entered
    status = Column(
        db_enum(AdvisoryStatus), nullable=False, server_default=AdvisoryStatus.PENDING.value, index=True
    )  # Request state
    missing_fields = Column(JSON, nullable=True)  # Fields to ask for when status is clarification_needed
    referral_reason = Column(Text, nullable=True)  # Reason when status is referred

    farmer = relationship("User", foreign_keys=[farmer_id])  # Farmer
    assisted_by = relationship("User", foreign_keys=[assisted_by_id])  # Agent
    farm = relationship("Farm")  # Farm
    crop_cycle = relationship("CropCycle", back_populates="advisory_requests")  # Season
    responses = relationship(
        "AdvisoryResponse", back_populates="request", cascade="all, delete-orphan"
    )  # Decisions for this request


class AdvisoryResponse(Base):  # The decision from the agronomic rules and resource checks
    __tablename__ = "advisory_responses"  # Table name

    id = Column(Integer, primary_key=True, index=True)  # ID field
    request_id = Column(
        Integer,
        ForeignKey("advisory_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )  # Parent request
    action = Column(Text, nullable=False)  # Action the farmer should take
    reason = Column(Text, nullable=False)  # Why the rules selected this action
    rule_ids = Column(JSON, nullable=True)  # Agronomic rules that produced the action
    applicable_crop_stage = Column(String(50), nullable=True)  # Stage the action is for
    suggested_timing = Column(String(255), nullable=True)  # When to do the action
    resource_requirements = Column(JSON, nullable=True)  # Items, quantities, and units
    affordability = Column(
        db_enum(Affordability),
        nullable=False,
        server_default=Affordability.UNDETERMINED.value,
    )  # Result of the budget check
    estimated_cost = Column(Numeric(12, 2), nullable=True)  # Total cost, if prices are known
    cost_assumptions = Column(Text, nullable=True)  # Prices, units, and dates in the cost
    weather_forecast_id = Column(
        Integer, ForeignKey("weather_forecasts.id"), nullable=True
    )  # Forecast used, if any
    weather_is_stale = Column(
        Boolean, nullable=True
    )  # True if the forecast was older than the freshness policy
    forecast_distance_km = Column(Float, nullable=True)  # Distance from the farm to the forecast point
    unresolved_assumptions = Column(JSON, nullable=True)  # Assumptions the farmer must confirm
    uncertainty_notes = Column(Text, nullable=True)  # Notes given to the model and the farmer
    expires_at = Column(DateTime, nullable=True)  # Cached advice is out of date after this time
    created_at = Column(DateTime, nullable=False, server_default=func.now())  # Decision time

    request = relationship("AdvisoryRequest", back_populates="responses")  # Parent request
    weather_forecast = relationship("WeatherForecast")  # Forecast used
    explanations = relationship(
        "AdvisoryExplanation", back_populates="response", cascade="all, delete-orphan"
    )  # Text the model wrote for this decision
    feedback = relationship(
        "AdvisoryFeedback", back_populates="response", cascade="all, delete-orphan"
    )  # What the farmer did


class AdvisoryExplanation(Base):  # Model text for a decision. A new row does not change the decision.
    __tablename__ = "advisory_explanations"  # Table name

    id = Column(Integer, primary_key=True, index=True)  # ID field
    response_id = Column(
        Integer,
        ForeignKey("advisory_responses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )  # Parent decision
    language = Column(String(10), nullable=False, server_default="en")  # Language code of the text
    text = Column(Text, nullable=False)  # Explanation shown to the farmer
    model_name = Column(String(100), nullable=False)  # For example "gemma"
    model_version = Column(String(50), nullable=True)  # Exact model version
    validation_status = Column(db_enum(ValidationStatus), nullable=False)  # Result of the output checks
    validation_notes = Column(JSON, nullable=True)  # Removed claims and failed checks
    is_current = Column(
        Boolean, nullable=False, server_default="1"
    )  # False after a newer explanation replaces it
    created_at = Column(DateTime, nullable=False, server_default=func.now())  # Generation time

    response = relationship("AdvisoryResponse", back_populates="explanations")  # Parent decision
    citations = relationship(
        "AdvisoryCitation", back_populates="explanation", cascade="all, delete-orphan"
    )  # Passages cited in the text


class AdvisoryCitation(Base):  # A passage that an explanation cites
    __tablename__ = "advisory_citations"  # Table name

    id = Column(Integer, primary_key=True, index=True)  # ID field
    explanation_id = Column(
        Integer,
        ForeignKey("advisory_explanations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )  # Parent explanation
    chunk_id = Column(
        Integer, ForeignKey("document_chunks.id"), nullable=False, index=True
    )  # Cited passage. No cascade, so old advice stays auditable.
    similarity_score = Column(Float, nullable=True)  # Retrieval similarity, not a probability
    rank = Column(Integer, nullable=True)  # Position in the retrieval results

    explanation = relationship("AdvisoryExplanation", back_populates="citations")  # Parent explanation
    chunk = relationship("DocumentChunk")  # Cited passage
