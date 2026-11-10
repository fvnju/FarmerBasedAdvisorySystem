"""Database queries for farms, farm resources, and soil records."""

from app.model.farm import Farm, FarmResource, SoilRecord
from app.repository.base import BaseRepository
from app.repository.scope import OwnerScope


def farm_owned_by(scope: OwnerScope):  # The farm belongs to the user or to an assigned farmer
    return scope.matches(Farm.owner_id)


class FarmRepository(BaseRepository[Farm]):
    model = Farm
    search_fields = (Farm.name, Farm.location_description)
    sort_fields = ("id", "name", "cultivated_area_ha", "created_at", "updated_at")

    def owner_condition(self, scope):
        return farm_owned_by(scope)


class FarmResourceRepository(BaseRepository[FarmResource]):
    model = FarmResource
    search_fields = (FarmResource.name, FarmResource.unit, FarmResource.notes)
    sort_fields = ("id", "name", "resource_type", "created_at", "updated_at")

    def owner_condition(self, scope):
        return FarmResource.farm.has(farm_owned_by(scope))


class SoilRecordRepository(BaseRepository[SoilRecord]):
    model = SoilRecord
    search_fields = (SoilRecord.property_name, SoilRecord.value_text, SoilRecord.source_note)
    sort_fields = ("id", "property_name", "measured_on", "created_at", "updated_at")

    def owner_condition(self, scope):
        return SoilRecord.farm.has(farm_owned_by(scope))
