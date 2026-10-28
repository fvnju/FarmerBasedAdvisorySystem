from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)  # Import column types
from sqlalchemy.orm import relationship  # Import relationship
from app.database import Base  # Import Base
from app.model.enums import (
    DataProvenance,
    ResourceType,
    WaterAccess,
    db_enum,
)  # Import enums
from app.model.mixins import TimestampMixin  # Import created_at and updated_at


class Farm(TimestampMixin, Base):  # Farm profile. Empty columns mean "unknown", never a guess.
    __tablename__ = "farms"  # Table name

    id = Column(Integer, primary_key=True, index=True)  # ID field
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )  # Farmer who owns the farm
    region_id = Column(
        Integer, ForeignKey("regions.id", ondelete="SET NULL"), nullable=True, index=True
    )  # Agroecological zone
    name = Column(String(100), nullable=False)  # Name the farmer uses
    latitude = Column(Numeric(9, 6), nullable=True)  # Approximate location, with consent only
    longitude = Column(Numeric(9, 6), nullable=True)  # Approximate location, with consent only
    location_description = Column(String(255), nullable=True)  # Village, ward, or LGA
    cultivated_area_ha = Column(Numeric(10, 2), nullable=True)  # Area in hectares
    water_access = Column(db_enum(WaterAccess), nullable=True)  # Main water source
    budget_min = Column(Numeric(12, 2), nullable=True)  # Lower end of the budget range
    budget_max = Column(Numeric(12, 2), nullable=True)  # Upper end of the budget range
    currency = Column(String(3), nullable=False, server_default="NGN")  # ISO 4217 code
    client_reference = Column(
        String(36), unique=True, nullable=True
    )  # UUID from the offline client, to stop duplicate syncs

    owner = relationship("User", back_populates="farms")  # Farmer
    region = relationship("Region", back_populates="farms")  # Zone
    resources = relationship(
        "FarmResource", back_populates="farm", cascade="all, delete-orphan"
    )  # Inputs, equipment, water, and labour
    soil_records = relationship(
        "SoilRecord", back_populates="farm", cascade="all, delete-orphan"
    )  # Soil values with provenance
    crop_cycles = relationship(
        "CropCycle", back_populates="farm", cascade="all, delete-orphan"
    )  # Seasons on this farm


class FarmResource(TimestampMixin, Base):  # One resource and whether the farmer has it
    __tablename__ = "farm_resources"  # Table name

    id = Column(Integer, primary_key=True, index=True)  # ID field
    farm_id = Column(
        Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True
    )  # Parent farm
    resource_type = Column(db_enum(ResourceType), nullable=False)  # Kind of resource
    name = Column(String(100), nullable=False)  # For example "NPK 15-15-15" or "knapsack sprayer"
    is_available = Column(Boolean, nullable=False)  # False records a known gap
    quantity = Column(Numeric(12, 2), nullable=True)  # Amount on hand
    unit = Column(String(20), nullable=True)  # Unit of the quantity, for example "kg"
    notes = Column(Text, nullable=True)  # Free text from the farmer

    farm = relationship("Farm", back_populates="resources")  # Parent farm


class SoilRecord(TimestampMixin, Base):  # One soil value and where it came from
    __tablename__ = "soil_records"  # Table name

    id = Column(Integer, primary_key=True, index=True)  # ID field
    farm_id = Column(
        Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True
    )  # Parent farm
    property_name = Column(String(50), nullable=False)  # For example "ph" or "nitrogen"
    value = Column(Numeric(12, 4), nullable=True)  # Numeric value, if known
    value_text = Column(String(100), nullable=True)  # Text value, for example "sandy loam"
    unit = Column(String(20), nullable=True)  # Unit of the value
    provenance = Column(db_enum(DataProvenance), nullable=False)  # Lab, farmer, or regional
    measured_on = Column(Date, nullable=True)  # Date of the test or estimate
    source_note = Column(String(255), nullable=True)  # Lab name or regional source

    farm = relationship("Farm", back_populates="soil_records")  # Parent farm
