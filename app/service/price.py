"""Business rules for price records."""

from app.model.enums import PriceSource
from app.model.price import PriceRecord
from app.repository.price import PriceRecordRepository
from app.schema.common import Operation
from app.service.base import BaseService


class PriceRecordService(BaseService[PriceRecord]):
    repository_class = PriceRecordRepository
    label = "Price record"
    module = "prices"
    permissions = {Operation.UPDATE: "prices.manage", Operation.DELETE: "prices.manage"}
    actor_fields = ("recorded_by_id",)

    def validate(self, values, current):
        self._not_in_future(values, "priced_on")
        if values["source"] == PriceSource.USER_QUOTATION:
            self._require_values(values, ["farm_id"], "Give the farm of the quotation.")
