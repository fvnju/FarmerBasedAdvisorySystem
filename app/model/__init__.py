from app.model.user import User  # Import User model
from app.model.role import Role  # Import Role model
from app.model.user_role import user_role_association  # Import association table
from app.model.modules import Module  # Import Module model
from app.model.privilege import Privilege  # Import Privilege model
from app.model.role_modules import role_modules_association  # Import association table
from app.model.role_privileges import role_privileges_association  # Import association table
from app.model.auth_token import RefreshToken, OneTimeToken  # Import token models
from app.model.consent import ConsentRecord  # Import consent model
from app.model.agent_assignment import AgentFarmerAssignment  # Import agent link model
from app.model.audit_log import AuditLog  # Import audit model
from app.model.region import Region  # Import Region model
from app.model.crop import Crop  # Import Crop model
from app.model.farm import Farm, FarmResource, SoilRecord  # Import farm profile models
from app.model.crop_cycle import CropCycle  # Import CropCycle model
from app.model.knowledge import KnowledgeDocument, DocumentChunk  # Import knowledge models
from app.model.weather import WeatherForecast, FreshnessPolicy  # Import weather models
from app.model.price import PriceRecord  # Import price model
from app.model.advisory import (
    AdvisoryRequest,
    AdvisoryResponse,
    AdvisoryExplanation,
    AdvisoryCitation,
)  # Import advisory models
from app.model.feedback import AdvisoryFeedback, FieldObservation  # Import feedback models
from app.model.alert import Alert  # Import Alert model

__all__ = [
    "User",
    "Role",
    "user_role_association",
    "Module",
    "Privilege",
    "role_modules_association",
    "role_privileges_association",
    "RefreshToken",
    "OneTimeToken",
    "ConsentRecord",
    "AgentFarmerAssignment",
    "AuditLog",
    "Region",
    "Crop",
    "Farm",
    "FarmResource",
    "SoilRecord",
    "CropCycle",
    "KnowledgeDocument",
    "DocumentChunk",
    "WeatherForecast",
    "FreshnessPolicy",
    "PriceRecord",
    "AdvisoryRequest",
    "AdvisoryResponse",
    "AdvisoryExplanation",
    "AdvisoryCitation",
    "AdvisoryFeedback",
    "FieldObservation",
    "Alert",
]  # Expose them for easy importing
