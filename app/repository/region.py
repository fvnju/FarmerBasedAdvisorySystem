"""Database queries for regions."""

from app.model.region import Region
from app.repository.base import BaseRepository


class RegionRepository(BaseRepository[Region]):
    model = Region
    search_fields = (Region.name, Region.description)
    sort_fields = ("id", "name")
