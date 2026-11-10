"""Database queries for crops."""

from app.model.crop import Crop
from app.repository.base import BaseRepository


class CropRepository(BaseRepository[Crop]):
    model = Crop
    search_fields = (Crop.name, Crop.scientific_name)
    sort_fields = ("id", "name")
