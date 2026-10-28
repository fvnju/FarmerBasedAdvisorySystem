from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, String, func  # Import column types
from sqlalchemy.orm import relationship  # Import relationship
from app.database import Base  # Import Base
from app.model.enums import PriceSource, db_enum  # Import enums


class PriceRecord(Base):  # A dated price for an input, used in the budget check
    __tablename__ = "price_records"  # Table name

    id = Column(Integer, primary_key=True, index=True)  # ID field
    item_name = Column(String(100), nullable=False, index=True)  # For example "urea"
    unit = Column(String(20), nullable=False)  # For example "50 kg bag"
    price = Column(Numeric(12, 2), nullable=False)  # Price for one unit
    currency = Column(String(3), nullable=False, server_default="NGN")  # ISO 4217 code
    source = Column(db_enum(PriceSource), nullable=False)  # Survey, official list, or quotation
    priced_on = Column(Date, nullable=False)  # Date the price was true
    region_id = Column(
        Integer, ForeignKey("regions.id", ondelete="SET NULL"), nullable=True
    )  # Market zone, empty for a national price
    farm_id = Column(
        Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=True
    )  # Set for a quotation that one farmer gave
    recorded_by_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )  # User who entered the price
    created_at = Column(DateTime, nullable=False, server_default=func.now())  # Entry time

    region = relationship("Region")  # Market zone
    farm = relationship("Farm")  # Farm for a quotation
