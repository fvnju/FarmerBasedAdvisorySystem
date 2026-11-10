"""Business rules for consent records.

A record is never changed or deleted, because it is the proof of consent.
To withdraw a consent, insert a new record with granted false.
"""

from app.model.consent import ConsentRecord
from app.repository.consent import ConsentRecordRepository
from app.schema.common import Operation
from app.service.base import BaseService


class ConsentRecordService(BaseService[ConsentRecord]):
    repository_class = ConsentRecordRepository
    operations = frozenset({Operation.LIST, Operation.READ, Operation.CREATE})
    label = "Consent record"
    module = "consents"

    def prepare(self, data, current):
        if self.actor is not None:  # An agent who records the consent of a farmer is named
            data["recorded_by_id"] = self.actor.id if self.actor.id != data["user_id"] else None
        return data
