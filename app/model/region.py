from sqlalchemy import Boolean, Column, Integer, String, Text  # Import column types
from sqlalchemy.orm import relationship  # Import relationship
from app.database import Base  # Import Base


class Region(Base):  # An agroecological zone that guidance applies to
    __tablename__ = "regions"  # Table name

    id = Column(Integer, primary_key=True, index=True)  # ID field
    name = Column(String(100), unique=True, index=True, nullable=False)  # Zone name
    description = Column(Text, nullable=True)  # Boundaries and notes
    is_supported = Column(
        Boolean, nullable=False, server_default="0"
    )  # True if the system gives advice for this zone

    farms = relationship("Farm", back_populates="region")  # Farms in the zone
    documents = relationship("KnowledgeDocument", back_populates="region")  # Guidance for the zone
