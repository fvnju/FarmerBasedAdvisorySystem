from sqlalchemy import Boolean, Column, Integer, String  # Import column types
from sqlalchemy.orm import relationship  # Import relationship
from app.database import Base  # Import Base


class Crop(Base):  # A crop the system knows about, for example maize
    __tablename__ = "crops"  # Table name

    id = Column(Integer, primary_key=True, index=True)  # ID field
    name = Column(String(100), unique=True, index=True, nullable=False)  # Common name
    scientific_name = Column(String(150), nullable=True)  # For example "Zea mays"
    is_supported = Column(
        Boolean, nullable=False, server_default="0"
    )  # True if the system gives advice for this crop

    crop_cycles = relationship("CropCycle", back_populates="crop")  # Seasons of this crop
    documents = relationship("KnowledgeDocument", back_populates="crop")  # Guidance for this crop
