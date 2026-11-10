"""Schemas for weather forecasts and freshness policies."""

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field

from app.model.enums import AdvisoryActionType, ForecastStatus
from app.schema.common import ListQuery, ReadSchema
from app.schema.fields import Latitude, Longitude

# Weather forecast. A forecast is never changed after it is saved.


class WeatherForecastCreate(BaseModel):
    provider: str = Field(min_length=1, max_length=50)
    latitude: Latitude
    longitude: Longitude
    coverage_description: str | None = Field(None, max_length=255)
    status: ForecastStatus
    error_message: str | None = None
    issued_at: datetime | None = None
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    payload: dict[str, Any] | list[Any] | None = None


class WeatherForecastRead(ReadSchema):
    id: int
    provider: str
    latitude: Decimal
    longitude: Decimal
    coverage_description: str | None
    status: ForecastStatus
    error_message: str | None
    issued_at: datetime | None
    retrieved_at: datetime
    valid_from: datetime | None
    valid_to: datetime | None
    payload: Any | None


class WeatherForecastListItem(ReadSchema):  # Page item without the payload, so the page stays small
    id: int
    provider: str
    latitude: Decimal
    longitude: Decimal
    status: ForecastStatus
    issued_at: datetime | None
    retrieved_at: datetime
    valid_from: datetime | None
    valid_to: datetime | None


class WeatherForecastQuery(ListQuery):
    provider: str | None = None
    status: ForecastStatus | None = None


# Freshness policy


class FreshnessPolicyCreate(BaseModel):
    action_type: AdvisoryActionType
    requires_forecast: bool
    max_forecast_age_hours: int | None = Field(None, gt=0)
    max_location_distance_km: int | None = Field(None, gt=0)


class FreshnessPolicyUpdate(BaseModel):
    action_type: AdvisoryActionType | None = None
    requires_forecast: bool | None = None
    max_forecast_age_hours: int | None = Field(None, gt=0)
    max_location_distance_km: int | None = Field(None, gt=0)


class FreshnessPolicyRead(ReadSchema):
    id: int
    action_type: AdvisoryActionType
    requires_forecast: bool
    max_forecast_age_hours: int | None
    max_location_distance_km: int | None


class FreshnessPolicyQuery(ListQuery):
    action_type: AdvisoryActionType | None = None
    requires_forecast: bool | None = None
