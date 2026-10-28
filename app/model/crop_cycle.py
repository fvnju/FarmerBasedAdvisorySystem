from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String  # Import column types
from sqlalchemy.orm import relationship  # Import relationship
from app.database import Base  # Import Base
from app.model.enums import CropCycleStatus, db_enum  # Import enums
from app.model.mixins import TimestampMixin  # Import created_at and updated_at


class CropCycle(TimestampMixin, Base):  # One growing season of one crop on one farm
    __tablename__ = "crop_cycles"  # Table name

    id = Column(Integer, primary_key=True, index=True)  # ID field
    farm_id = Column(
        Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True
    )  # Parent farm
    crop_id = Column(
        Integer, ForeignKey("crops.id"), nullable=False, index=True
    )  # Crop grown
    season_label = Column(String(50), nullable=True)  # For example "2026 wet season"
    planting_date = Column(Date, nullable=True)  # Empty if not planted or not known
    crop_stage = Column(String(50), nullable=True)  # For example "vegetative" or "tasseling"
    stage_updated_at = Column(DateTime, nullable=True)  # When the stage was last reported
    status = Column(
        db_enum(CropCycleStatus), nullable=False, server_default=CropCycleStatus.ACTIVE.value
    )  # Active, completed, or abandoned
    ended_on = Column(Date, nullable=True)  # Harvest or abandon date

    farm = relationship("Farm", back_populates="crop_cycles")  # Parent farm
    crop = relationship("Crop", back_populates="crop_cycles")  # Crop
    advisory_requests = relationship(
        "AdvisoryRequest", back_populates="crop_cycle"
    )  # Questions asked during this season
    observations = relationship(
        "FieldObservation", back_populates="crop_cycle"
    )  # Observations during this season
