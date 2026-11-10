"""Routes for knowledge documents, document chunks."""

from app.controller.knowledge import (
    DocumentChunkController,
    KnowledgeDocumentController,
)
from app.route.factory import build_crud_router

routers = [
    build_crud_router(KnowledgeDocumentController, prefix="/knowledge-documents", tag="Knowledge documents"),
    build_crud_router(DocumentChunkController, prefix="/document-chunks", tag="Document chunks"),
]
