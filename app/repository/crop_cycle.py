"""Database queries for crop cycles."""

from app.model.crop_cycle import CropCycle
from app.repository.base import BaseRepository
from app.repository.farm import farm_owned_by


class CropCycleRepository(BaseRepository[CropCycle]):
    model = CropCycle
    search_fields = (CropCycle.season_label, CropCycle.crop_stage)
    sort_fields = ("id", "planting_date", "ended_on", "created_at", "updated_at")

    def owner_condition(self, scope):
        return CropCycle.farm.has(farm_owned_by(scope))
