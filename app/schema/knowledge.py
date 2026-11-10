"""Schemas for knowledge documents and document chunks."""

from datetime import date, datetime

from pydantic import BaseModel, Field

from app.model.enums import ReviewStatus
from app.schema.common import ListQuery, ReadSchema
from app.schema.fields import Id

# Knowledge document. The upload process sets file_path, so the API does not take it.


class KnowledgeDocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    source_organization: str | None = Field(None, max_length=150)
    source_url: str | None = Field(None, max_length=500, pattern=r"^https?://")
    crop_id: Id | None = Field(None, description="Empty means all crops")
    region_id: Id | None = Field(None, description="Empty means all regions")
    version: str = Field("1", min_length=1, max_length=20)
    published_on: date | None = None
    revised_on: date | None = None
    uploaded_by_id: Id | None = None


class KnowledgeDocumentUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    source_organization: str | None = Field(None, max_length=150)
    source_url: str | None = Field(None, max_length=500, pattern=r"^https?://")
    crop_id: Id | None = None
    region_id: Id | None = None
    version: str | None = Field(None, min_length=1, max_length=20)
    published_on: date | None = None
    revised_on: date | None = None
    review_status: ReviewStatus | None = None
    reviewed_by_id: Id | None = None
    review_notes: str | None = None
    superseded_by_id: Id | None = None


class KnowledgeDocumentRead(ReadSchema):
    id: int
    title: str
    source_organization: str | None
    source_url: str | None
    file_path: str | None
    crop_id: int | None
    region_id: int | None
    version: str
    published_on: date | None
    revised_on: date | None
    review_status: ReviewStatus
    reviewed_by_id: int | None
    reviewed_at: datetime | None
    review_notes: str | None
    superseded_by_id: int | None
    uploaded_by_id: int | None
    created_at: datetime
    updated_at: datetime


class KnowledgeDocumentQuery(ListQuery):
    crop_id: int | None = None
    region_id: int | None = None
    review_status: ReviewStatus | None = None
    uploaded_by_id: int | None = None


# Document chunk. The embedding is large, so responses do not include it.


class DocumentChunkCreate(BaseModel):
    document_id: Id
    chunk_index: int = Field(ge=0)
    section_title: str | None = Field(None, max_length=255)
    content: str = Field(min_length=1)
    token_count: int | None = Field(None, ge=0)
    embedding: list[float] | None = None
    embedding_model: str | None = Field(None, max_length=100)


class DocumentChunkUpdate(BaseModel):
    section_title: str | None = Field(None, max_length=255)
    content: str | None = Field(None, min_length=1)
    token_count: int | None = Field(None, ge=0)
    embedding: list[float] | None = None
    embedding_model: str | None = Field(None, max_length=100)


class DocumentChunkRead(ReadSchema):
    id: int
    document_id: int
    chunk_index: int
    section_title: str | None
    content: str
    content_hash: str
    token_count: int | None
    embedding_model: str | None


class DocumentChunkQuery(ListQuery):
    document_id: int | None = None
    embedding_model: str | None = None
