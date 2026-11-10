"""Controllers for knowledge documents, document chunks."""

from app.controller.base import BaseController
from app.schema.knowledge import (
    DocumentChunkCreate,
    DocumentChunkQuery,
    DocumentChunkRead,
    DocumentChunkUpdate,
    KnowledgeDocumentCreate,
    KnowledgeDocumentQuery,
    KnowledgeDocumentRead,
    KnowledgeDocumentUpdate,
)
from app.service.knowledge import (
    DocumentChunkService,
    KnowledgeDocumentService,
)


class KnowledgeDocumentController(BaseController):
    service_class = KnowledgeDocumentService
    read_schema = KnowledgeDocumentRead
    create_schema = KnowledgeDocumentCreate
    update_schema = KnowledgeDocumentUpdate
    query_schema = KnowledgeDocumentQuery


class DocumentChunkController(BaseController):
    service_class = DocumentChunkService
    read_schema = DocumentChunkRead
    create_schema = DocumentChunkCreate
    update_schema = DocumentChunkUpdate
    query_schema = DocumentChunkQuery
