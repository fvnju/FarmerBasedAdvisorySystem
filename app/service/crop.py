"""Business rules for crops."""

from app.model.crop import Crop
from app.repository.crop import CropRepository
from app.service.base import BaseService
from app.service.region import REFERENCE_PERMISSIONS


class CropService(BaseService[Crop]):
    repository_class = CropRepository
    label = "Crop"
    permissions = REFERENCE_PERMISSIONS
