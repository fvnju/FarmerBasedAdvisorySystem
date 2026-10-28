from sqlalchemy import (
    JSON,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)  # Import column types
from sqlalchemy.orm import relationship  # Import relationship
from app.database import Base  # Import Base
from app.model.enums import ReviewStatus, db_enum  # Import enums
from app.model.mixins import TimestampMixin  # Import created_at and updated_at


class KnowledgeDocument(TimestampMixin, Base):  # Crop guidance. Only approved documents are retrieved.
    __tablename__ = "knowledge_documents"  # Table name

    id = Column(Integer, primary_key=True, index=True)  # ID field
    title = Column(String(255), nullable=False)  # Document title
    source_organization = Column(String(150), nullable=True)  # Publisher, for example an extension service
    source_url = Column(String(500), nullable=True)  # Link to the original
    file_path = Column(String(500), nullable=True)  # Stored copy of the file
    crop_id = Column(
        Integer, ForeignKey("crops.id", ondelete="SET NULL"), nullable=True, index=True
    )  # Empty means the document applies to all crops
    region_id = Column(
        Integer, ForeignKey("regions.id", ondelete="SET NULL"), nullable=True, index=True
    )  # Empty means the document applies to all regions
    version = Column(String(20), nullable=False, server_default="1")  # Edition or revision
    published_on = Column(Date, nullable=True)  # Publication date
    revised_on = Column(Date, nullable=True)  # Last revision date
    review_status = Column(
        db_enum(ReviewStatus), nullable=False, server_default=ReviewStatus.DRAFT.value, index=True
    )  # Specialist review state
    reviewed_by_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )  # Specialist who approved or rejected it
    reviewed_at = Column(DateTime, nullable=True)  # Time of the review
    review_notes = Column(Text, nullable=True)  # Reason for the decision
    superseded_by_id = Column(
        Integer, ForeignKey("knowledge_documents.id", ondelete="SET NULL"), nullable=True
    )  # Newer document that replaces this one
    uploaded_by_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )  # User who added the document

    crop = relationship("Crop", back_populates="documents")  # Crop
    region = relationship("Region", back_populates="documents")  # Region
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id])  # Reviewer
    uploaded_by = relationship("User", foreign_keys=[uploaded_by_id])  # Uploader
    superseded_by = relationship(
        "KnowledgeDocument", remote_side=[id]
    )  # Replacement document
    chunks = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan"
    )  # Passages for retrieval


class DocumentChunk(Base):  # One passage of a document, with its embedding
    __tablename__ = "document_chunks"  # Table name
    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="uq_chunk_position"),
    )  # One chunk at each position

    id = Column(Integer, primary_key=True, index=True)  # ID field, cited in advice
    document_id = Column(
        Integer,
        ForeignKey("knowledge_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )  # Parent document
    chunk_index = Column(Integer, nullable=False)  # Position in the document
    section_title = Column(String(255), nullable=True)  # Heading the passage is under
    content = Column(Text, nullable=False)  # Passage text
    content_hash = Column(String(64), nullable=False, index=True)  # SHA-256, to find duplicates
    token_count = Column(Integer, nullable=True)  # Length for the model context
    embedding = Column(JSON, nullable=True)  # Vector as a list of floats
    embedding_model = Column(String(100), nullable=True)  # Model that made the vector

    document = relationship("KnowledgeDocument", back_populates="chunks")  # Parent document
