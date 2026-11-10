"""Business rules for farms, farm resources, and soil records."""

from app.core.exceptions import InvalidInputError
from app.model.farm import Farm, FarmResource, SoilRecord
from app.repository.farm import FarmRepository, FarmResourceRepository, SoilRecordRepository
from app.service.base import BaseService


class FarmService(BaseService[Farm]):
    repository_class = FarmRepository
    label = "Farm"
    module = "farms"

    def validate(self, values, current):
        budget_min, budget_max = values["budget_min"], values["budget_max"]
        if budget_min is not None and budget_max is not None and budget_min > budget_max:
            raise InvalidInputError(
                "budget_min must not be more than budget_max.", {"fields": ["budget_min", "budget_max"]}
            )
        if (values["latitude"] is None) != (values["longitude"] is None):
            raise InvalidInputError(
                "Give the latitude and the longitude together, or neither.",
                {"fields": ["latitude", "longitude"]},
            )


class FarmResourceService(BaseService[FarmResource]):
    repository_class = FarmResourceRepository
    label = "Farm resource"
    module = "farms"

    def validate(self, values, current):
        if values["quantity"] is not None:
            self._require_values(values, ["unit"], "Give the unit of the quantity.")


class SoilRecordService(BaseService[SoilRecord]):
    repository_class = SoilRecordRepository
    label = "Soil record"
    module = "farms"

    def validate(self, values, current):
        if values["value"] is None and not values["value_text"]:
            raise InvalidInputError(
                "Give a numeric value or a text value.", {"fields": ["value", "value_text"]}
            )
        self._not_in_future(values, "measured_on")
