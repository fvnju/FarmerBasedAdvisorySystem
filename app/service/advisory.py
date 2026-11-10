"""Business rules for advisory requests, responses, explanations, and citations."""

from app.core.exceptions import InvalidInputError
from app.model.advisory import (
    AdvisoryCitation,
    AdvisoryExplanation,
    AdvisoryRequest,
    AdvisoryResponse,
)
from app.model.enums import AccessMode, AdvisoryStatus, Affordability, ReviewStatus
from app.repository.advisory import (
    AdvisoryCitationRepository,
    AdvisoryExplanationRepository,
    AdvisoryRequestRepository,
    AdvisoryResponseRepository,
)
from app.repository.crop_cycle import CropCycleRepository
from app.repository.farm import FarmRepository
from app.repository.knowledge import DocumentChunkRepository
from app.schema.common import Operation
from app.service.base import BaseService


RESPOND_PERMISSIONS = {  # Responses, explanations, and citations come from the advisory engine or a specialist
    Operation.CREATE: "advisories.respond",
    Operation.UPDATE: "advisories.respond",
    Operation.DELETE: "advisories.delete",
}
STATUS_FIELDS = {"status", "missing_fields", "referral_reason"}

class AdvisoryRequestService(BaseService[AdvisoryRequest]):
    repository_class = AdvisoryRequestRepository
    label = "Advisory request"
    module = "advisories"
    permissions = {
        Operation.CREATE: "advisories.request",
        Operation.UPDATE: "advisories.request",
    }

    def prepare(self, data, current):
        if STATUS_FIELDS & data.keys():
            self._require_privilege("advisories.respond")
        if current is None and self.actor is not None and data["farmer_id"] != self.actor.id:
            data["access_mode"] = AccessMode.ASSISTED  # Someone else asks for the farmer
            if self.is_scoped or data.get("assisted_by_id") is None:
                data["assisted_by_id"] = self.actor.id
        return data

    def validate(self, values, current):
        self._check_access(values)
        self._check_farm_and_cycle(values)
        status = values["status"]
        if status == AdvisoryStatus.CLARIFICATION_NEEDED:
            self._require_values(values, ["missing_fields"], "Give the fields that the farmer must supply.")
        if status == AdvisoryStatus.REFERRED:
            self._require_values(values, ["referral_reason"], "Give the reason for the referral.")

    def _check_access(self, values):
        assisted_by_id = values["assisted_by_id"]
        if values["access_mode"] == AccessMode.ASSISTED:
            self._require_values(values, ["assisted_by_id"], "Give the agent who helped the farmer.")
            if assisted_by_id == values["farmer_id"]:
                raise InvalidInputError("The farmer cannot be the assisting agent.", {"fields": ["assisted_by_id"]})
        elif assisted_by_id is not None:
            raise InvalidInputError(
                "An independent request cannot have an assisting agent.", {"fields": ["assisted_by_id"]}
            )

    def _check_farm_and_cycle(self, values):  # The farm must belong to the farmer, the cycle to the farm
        if not any(values.changed(field) for field in ("farmer_id", "farm_id", "crop_cycle_id")):
            return
        farm_id, crop_cycle_id = values["farm_id"], values["crop_cycle_id"]
        if farm_id is not None:
            farm = self._get_linked(FarmRepository(self.db), farm_id, "Farm")
            if farm.owner_id != values["farmer_id"]:
                raise InvalidInputError("The farm does not belong to this farmer.", {"fields": ["farm_id"]})
        if crop_cycle_id is not None:
            if farm_id is None:
                raise InvalidInputError("Give the farm of the crop cycle.", {"fields": ["farm_id"]})
            cycle = self._get_linked(CropCycleRepository(self.db), crop_cycle_id, "Crop cycle")
            if cycle.farm_id != farm_id:
                raise InvalidInputError("The crop cycle is not on this farm.", {"fields": ["crop_cycle_id"]})


class AdvisoryResponseService(BaseService[AdvisoryResponse]):
    repository_class = AdvisoryResponseRepository
    label = "Advisory response"
    module = "advisories"
    permissions = RESPOND_PERMISSIONS

    def validate(self, values, current):
        if values["affordability"] in (Affordability.AFFORDABLE, Affordability.UNAFFORDABLE):
            self._require_values(values, ["estimated_cost"], "Give the estimated cost for the budget result.")
        if values["estimated_cost"] is not None:
            self._require_values(values, ["cost_assumptions"], "Give the prices and dates that the cost uses.")

    def after_save(self, item, created):
        if not created:
            return
        requests = AdvisoryRequestRepository(self.db)
        request = requests.get(item.request_id)
        if request is not None and request.status == AdvisoryStatus.PENDING:
            requests.update(request, {"status": AdvisoryStatus.ANSWERED})  # The request now has a decision


class AdvisoryExplanationService(BaseService[AdvisoryExplanation]):
    repository_class = AdvisoryExplanationRepository
    label = "Advisory explanation"
    module = "advisories"
    permissions = RESPOND_PERMISSIONS

    def after_save(self, item, created):
        if not item.is_current:
            return
        for other in self.repo.current_for(item.response_id, item.language):  # One current text for each language
            if other.id != item.id:
                self.repo.update(other, {"is_current": False})


class AdvisoryCitationService(BaseService[AdvisoryCitation]):
    repository_class = AdvisoryCitationRepository
    label = "Advisory citation"
    module = "advisories"
    permissions = RESPOND_PERMISSIONS

    def validate(self, values, current):
        if not values.changed("chunk_id"):
            return
        chunk = self._get_linked(DocumentChunkRepository(self.db), values["chunk_id"], "Document chunk")
        if chunk.document.review_status != ReviewStatus.APPROVED:
            raise InvalidInputError(
                "Advice can cite only passages from approved documents.", {"fields": ["chunk_id"]}
            )
