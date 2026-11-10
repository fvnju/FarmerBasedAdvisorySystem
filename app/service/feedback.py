"""Business rules for advisory feedback and field observations."""

from app.core.exceptions import InvalidInputError
from app.model.enums import FeedbackOutcome
from app.model.feedback import AdvisoryFeedback, FieldObservation
from app.repository.feedback import AdvisoryFeedbackRepository, FieldObservationRepository
from app.schema.common import Operation
from app.service.base import BaseService


FEEDBACK_PERMISSIONS = {
    Operation.CREATE: "advisories.give_feedback",
    Operation.UPDATE: "advisories.give_feedback",
    Operation.DELETE: "advisories.delete",
}

class AdvisoryFeedbackService(BaseService[AdvisoryFeedback]):
    repository_class = AdvisoryFeedbackRepository
    label = "Advisory feedback"
    module = "advisories"
    permissions = FEEDBACK_PERMISSIONS
    actor_fields = ("recorded_by_id",)

    def validate(self, values, current):
        outcome = values["outcome"]
        if outcome in (FeedbackOutcome.MODIFIED, FeedbackOutcome.REJECTED):
            self._require_values(values, ["reason"], "Give the reason the farmer changed or rejected the advice.")
        if outcome == FeedbackOutcome.NOT_YET and values["action_date"] is not None:
            raise InvalidInputError("An action that is not done cannot have a date.", {"fields": ["action_date"]})
        self._not_in_future(values, "action_date")


class FieldObservationService(BaseService[FieldObservation]):
    repository_class = FieldObservationRepository
    label = "Field observation"
    module = "advisories"
    permissions = FEEDBACK_PERMISSIONS
    actor_fields = ("recorded_by_id",)

    def prepare(self, data, current):
        if {"is_verified", "verified_by_id"} & data.keys():
            self._require_privilege("advisories.review")
            if data.get("is_verified") and self.actor is not None and data.get("verified_by_id") is None:
                data["verified_by_id"] = self.actor.id
        if data.get("is_verified") is False:
            data["verified_by_id"] = None  # An unverified value has no verifier
        return data

    def validate(self, values, current):
        if values["is_verified"]:
            self._require_values(values, ["verified_by_id"], "Give the specialist who verified the observation.")
        self._not_in_future(values, "observed_on")
