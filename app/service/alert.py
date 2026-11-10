"""Business rules for alerts."""

from app.core.exceptions import ConflictError, InvalidInputError
from app.model.alert import Alert
from app.model.enums import AlertStatus, ConsentType
from app.repository.alert import AlertRepository
from app.repository.consent import ConsentRecordRepository
from app.schema.common import Operation
from app.service.base import BaseService
from app.util.time import utc_now


class AlertService(BaseService[Alert]):
    repository_class = AlertRepository
    label = "Alert"
    module = "alerts"
    permissions = {
        Operation.CREATE: "alerts.manage",
        Operation.UPDATE: "alerts.read",  # A user can mark an alert as read. Other fields need alerts.manage.
        Operation.DELETE: "alerts.manage",
    }

    def prepare(self, data, current):
        if current is not None and data.keys() - {"read_at"}:
            self._require_privilege("alerts.manage")
        if data.get("status") == AlertStatus.SENT and (current is None or current.sent_at is None):
            data["sent_at"] = utc_now()
        return data

    def validate(self, values, current):
        scheduled_for, expires_at = values["scheduled_for"], values["expires_at"]
        if scheduled_for is not None and expires_at is not None and expires_at <= scheduled_for:
            raise InvalidInputError("expires_at must be after scheduled_for.", {"fields": ["expires_at"]})
        if current is None:
            self._check_consent(values["user_id"])

    def _check_consent(self, user_id):  # Send alerts only to users whose last decision is a grant
        consent = ConsentRecordRepository(self.db).latest(user_id, ConsentType.ALERTS)
        if consent is None or not consent.granted:
            raise ConflictError(f"User {user_id} has not given consent for alerts.")
