"""Business rules for knowledge documents and document chunks."""

import hashlib

from app.core.exceptions import InvalidInputError
from app.model.enums import ReviewStatus
from app.model.knowledge import DocumentChunk, KnowledgeDocument
from app.repository.knowledge import DocumentChunkRepository, KnowledgeDocumentRepository
from app.schema.common import Operation
from app.service.base import BaseService
from app.util.time import utc_now

DECIDED = {ReviewStatus.APPROVED, ReviewStatus.REJECTED}


KNOWLEDGE_PERMISSIONS = {
    Operation.CREATE: "knowledge.upload",
    Operation.UPDATE: "knowledge.upload",
    Operation.DELETE: "knowledge.manage",
}
REVIEW_FIELDS = {"review_status", "reviewed_by_id", "review_notes"}

class KnowledgeDocumentService(BaseService[KnowledgeDocument]):
    repository_class = KnowledgeDocumentRepository
    label = "Knowledge document"
    module = "knowledge"
    permissions = KNOWLEDGE_PERMISSIONS
    actor_fields = ("uploaded_by_id",)

    def prepare(self, data, current):
        if REVIEW_FIELDS & data.keys():
            self._require_privilege("knowledge.review")
            if self.actor is not None and data.get("reviewed_by_id") is None:
                data["reviewed_by_id"] = self.actor.id
        if data.get("review_status") in DECIDED and (
            current is None or current.review_status != data["review_status"]
        ):
            data["reviewed_at"] = utc_now()  # Time of the specialist decision
        return data

    def validate(self, values, current):
        status = values["review_status"]
        if status in DECIDED:
            self._require_values(values, ["reviewed_by_id"], "Give the specialist who reviewed the document.")
        if status == ReviewStatus.REJECTED:
            self._require_values(values, ["review_notes"], "Give the reason for the rejection.")
        if current is not None and values["superseded_by_id"] == current.id:
            raise InvalidInputError("A document cannot replace itself.", {"fields": ["superseded_by_id"]})
        published_on, revised_on = values["published_on"], values["revised_on"]
        if published_on is not None and revised_on is not None and revised_on < published_on:
            raise InvalidInputError("revised_on must not be before published_on.", {"fields": ["revised_on"]})


class DocumentChunkService(BaseService[DocumentChunk]):
    repository_class = DocumentChunkRepository
    label = "Document chunk"
    module = "knowledge"
    permissions = KNOWLEDGE_PERMISSIONS

    def prepare(self, data, current):
        if data.get("content"):
            data["content_hash"] = hashlib.sha256(data["content"].encode()).hexdigest()  # Finds duplicates
        return data

    def validate(self, values, current):
        if values.changed("embedding") and values["embedding"]:
            self._require_values(values, ["embedding_model"], "Give the model that made the embedding.")
