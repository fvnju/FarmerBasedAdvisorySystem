"""Business rules for regions."""

from app.model.region import Region
from app.repository.region import RegionRepository
from app.schema.common import Operation
from app.service.base import BaseService

REFERENCE_PERMISSIONS = {
    Operation.LIST: "reference.read",
    Operation.READ: "reference.read",
    Operation.CREATE: "reference.manage",
    Operation.UPDATE: "reference.manage",
    Operation.DELETE: "reference.manage",
}


class RegionService(BaseService[Region]):
    repository_class = RegionRepository
    label = "Region"
    permissions = REFERENCE_PERMISSIONS
