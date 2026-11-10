"""Business rules for crop cycles."""

from app.core.exceptions import InvalidInputError
from app.model.crop_cycle import CropCycle
from app.model.enums import CropCycleStatus
from app.repository.crop_cycle import CropCycleRepository
from app.service.base import BaseService
from app.util.time import utc_now


class CropCycleService(BaseService[CropCycle]):
    repository_class = CropCycleRepository
    label = "Crop cycle"
    module = "farms"

    def prepare(self, data, current):
        if data.get("crop_stage") is not None and (current is None or current.crop_stage != data["crop_stage"]):
            data["stage_updated_at"] = utc_now()  # Lets the advice show how old the stage is
        return data

    def validate(self, values, current):
        status = values["status"] or CropCycleStatus.ACTIVE
        planting_date, ended_on = values["planting_date"], values["ended_on"]
        if status == CropCycleStatus.ACTIVE and ended_on is not None:
            raise InvalidInputError("An active crop cycle cannot have an end date.", {"fields": ["ended_on"]})
        if status == CropCycleStatus.COMPLETED:
            self._require_values(values, ["ended_on"], "Give the harvest date of a completed crop cycle.")
        if planting_date is not None and ended_on is not None and ended_on < planting_date:
            raise InvalidInputError("ended_on must not be before planting_date.", {"fields": ["ended_on"]})
        self._not_in_future(values, "planting_date", "ended_on")
