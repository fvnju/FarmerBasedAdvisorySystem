"""Database queries for advisory feedback and field observations."""

from app.model.crop_cycle import CropCycle
from app.model.feedback import AdvisoryFeedback, FieldObservation
from app.repository.advisory import response_owned_by
from app.repository.base import BaseRepository
from app.repository.farm import farm_owned_by


class AdvisoryFeedbackRepository(BaseRepository[AdvisoryFeedback]):
    model = AdvisoryFeedback
    search_fields = (AdvisoryFeedback.reason,)
    sort_fields = ("id", "action_date", "created_at")

    def owner_condition(self, scope):
        return AdvisoryFeedback.response.has(response_owned_by(scope))


class FieldObservationRepository(BaseRepository[FieldObservation]):
    model = FieldObservation
    search_fields = (FieldObservation.observation,)
    sort_fields = ("id", "observed_on", "created_at")

    def owner_condition(self, scope):
        return FieldObservation.crop_cycle.has(CropCycle.farm.has(farm_owned_by(scope)))
