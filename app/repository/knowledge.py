"""Database queries for knowledge documents and document chunks."""

from sqlalchemy.orm import defer

from app.model.knowledge import DocumentChunk, KnowledgeDocument
from app.repository.base import BaseRepository


class KnowledgeDocumentRepository(BaseRepository[KnowledgeDocument]):
    model = KnowledgeDocument
    search_fields = (KnowledgeDocument.title, KnowledgeDocument.source_organization)
    sort_fields = ("id", "title", "published_on", "revised_on", "created_at", "updated_at")


class DocumentChunkRepository(BaseRepository[DocumentChunk]):
    model = DocumentChunk
    search_fields = (DocumentChunk.section_title, DocumentChunk.content)
    sort_fields = ("id", "document_id", "chunk_index")
    load_options = (defer(DocumentChunk.embedding),)  # Responses do not show the vector
