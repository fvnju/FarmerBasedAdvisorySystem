import enum  # Import enum to define fixed sets of values
from sqlalchemy import Enum  # Import the SQLAlchemy Enum column type


def db_enum(enum_class):  # Build a column type that stores the enum value, not the name
    return Enum(
        enum_class,
        values_callable=lambda members: [member.value for member in members],
        native_enum=True,
        validate_strings=True,
    )


class WaterAccess(str, enum.Enum):  # How the farm gets water
    RAINFED = "rainfed"
    IRRIGATED = "irrigated"
    MIXED = "mixed"


class ResourceType(str, enum.Enum):  # Kind of resource a farm has
    INPUT = "input"  # Seed, fertilizer, chemicals
    EQUIPMENT = "equipment"
    WATER = "water"
    LABOUR = "labour"
    OTHER = "other"


class DataProvenance(str, enum.Enum):  # Where a soil value came from
    LAB_TEST = "lab_test"
    FARMER_ESTIMATE = "farmer_estimate"
    REGIONAL_SOURCE = "regional_source"


class CropCycleStatus(str, enum.Enum):  # State of one growing season
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class ReviewStatus(str, enum.Enum):  # Specialist review state of a knowledge document
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"  # Superseded, kept for audit only


class AdvisoryActionType(str, enum.Enum):  # Type of action the farmer asks about
    PLANTING = "planting"
    FERTILIZER = "fertilizer"
    IRRIGATION = "irrigation"
    PEST_DISEASE_TRIAGE = "pest_disease_triage"
    WEED_CONTROL = "weed_control"
    HARVEST = "harvest"
    GENERAL = "general"


class AccessMode(str, enum.Enum):  # Who used the service to make the request
    INDEPENDENT = "independent"
    ASSISTED = "assisted"  # An extension agent helped the farmer


class AdvisoryStatus(str, enum.Enum):  # State of an advisory request
    PENDING = "pending"
    ANSWERED = "answered"
    CLARIFICATION_NEEDED = "clarification_needed"
    REFERRED = "referred"  # Sent to a specialist
    FAILED = "failed"


class Affordability(str, enum.Enum):  # Result of the budget check
    AFFORDABLE = "affordable"
    UNAFFORDABLE = "unaffordable"
    UNDETERMINED = "undetermined"  # No cost data


class ValidationStatus(str, enum.Enum):  # Result of the output validation
    PASSED = "passed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"


class FeedbackOutcome(str, enum.Enum):  # What the farmer did with the advice
    FOLLOWED = "followed"
    MODIFIED = "modified"
    REJECTED = "rejected"
    NOT_YET = "not_yet"


class ForecastStatus(str, enum.Enum):  # Result of a forecast fetch
    OK = "ok"
    FAILED = "failed"


class PriceSource(str, enum.Enum):  # Where a price record came from
    MARKET_SURVEY = "market_survey"
    OFFICIAL_LIST = "official_list"
    USER_QUOTATION = "user_quotation"


class AlertChannel(str, enum.Enum):  # How an alert is delivered
    IN_APP = "in_app"
    SMS = "sms"
    PUSH = "push"
    EMAIL = "email"


class AlertStatus(str, enum.Enum):  # Delivery state of an alert
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ConsentType(str, enum.Enum):  # What the user agrees to
    LOCATION = "location"
    CONTACT_DETAILS = "contact_details"
    FARM_HISTORY = "farm_history"
    ALERTS = "alerts"
    RESEARCH_USE = "research_use"


class TokenPurpose(str, enum.Enum):  # Use of a one-time token
    EMAIL_VERIFICATION = "email_verification"
    PHONE_VERIFICATION = "phone_verification"
    PASSWORD_RESET = "password_reset"
