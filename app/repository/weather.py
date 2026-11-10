"""Database queries for weather forecasts and freshness policies."""

from sqlalchemy.orm import defer

from app.model.weather import FreshnessPolicy, WeatherForecast
from app.repository.base import BaseRepository


class WeatherForecastRepository(BaseRepository[WeatherForecast]):
    model = WeatherForecast
    search_fields = (WeatherForecast.provider, WeatherForecast.coverage_description)
    sort_fields = ("id", "retrieved_at", "issued_at", "valid_from")
    list_options = (  # A page does not show these large columns, so do not load them
        defer(WeatherForecast.payload),
        defer(WeatherForecast.error_message),
        defer(WeatherForecast.coverage_description),
    )


class FreshnessPolicyRepository(BaseRepository[FreshnessPolicy]):
    model = FreshnessPolicy
    sort_fields = ("id", "action_type")
