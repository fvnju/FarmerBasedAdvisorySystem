"""Database queries for price records."""

from sqlalchemy import or_

from app.model.price import PriceRecord
from app.repository.base import BaseRepository
from app.repository.farm import farm_owned_by


class PriceRecordRepository(BaseRepository[PriceRecord]):
    model = PriceRecord
    search_fields = (PriceRecord.item_name, PriceRecord.unit)
    sort_fields = ("id", "item_name", "price", "priced_on", "created_at")

    def owner_condition(self, scope):  # Market prices for all users, quotations only for their farm
        return or_(PriceRecord.farm_id.is_(None), PriceRecord.farm.has(farm_owned_by(scope)))
