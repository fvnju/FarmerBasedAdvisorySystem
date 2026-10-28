from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Integer,
    Numeric,
    String,
    Text,
    func,
)  # Import column types
from app.database import Base  # Import Base
from app.model.enums import AdvisoryActionType, ForecastStatus, db_enum  # Import enums


class WeatherForecast(Base):  # One forecast fetch from a provider. Rows are never updated.
    __tablename__ = "weather_forecasts"  # Table name

    id = Column(Integer, primary_key=True, index=True)  # ID field
    provider = Column(String(50), nullable=False)  # Weather API name
    latitude = Column(Numeric(9, 6), nullable=False)  # Point of the forecast
    longitude = Column(Numeric(9, 6), nullable=False)  # Point of the forecast
    coverage_description = Column(String(255), nullable=True)  # Grid size or station name
    status = Column(db_enum(ForecastStatus), nullable=False)  # OK or failed
    error_message = Column(Text, nullable=True)  # Provider error, if failed
    issued_at = Column(DateTime, nullable=True)  # Time the provider made the forecast
    retrieved_at = Column(
        DateTime, nullable=False, server_default=func.now(), index=True
    )  # Time this system got the forecast
    valid_from = Column(DateTime, nullable=True)  # Start of the forecast interval
    valid_to = Column(DateTime, nullable=True)  # End of the forecast interval
    payload = Column(JSON, nullable=True)  # Forecast data from the provider


class FreshnessPolicy(Base):  # Maximum forecast age for each advisory action
    __tablename__ = "freshness_policies"  # Table name

    id = Column(Integer, primary_key=True, index=True)  # ID field
    action_type = Column(
        db_enum(AdvisoryActionType), unique=True, nullable=False
    )  # Action the policy applies to
    requires_forecast = Column(Boolean, nullable=False)  # False if weather does not affect the action
    max_forecast_age_hours = Column(Integer, nullable=True)  # Older forecasts are stale
    max_location_distance_km = Column(Integer, nullable=True)  # Farther forecasts show a warning
