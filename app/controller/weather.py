"""Controllers for weather forecasts, freshness policies."""

from app.controller.base import BaseController
from app.schema.weather import (
    FreshnessPolicyCreate,
    FreshnessPolicyQuery,
    FreshnessPolicyRead,
    FreshnessPolicyUpdate,
    WeatherForecastCreate,
    WeatherForecastListItem,
    WeatherForecastQuery,
    WeatherForecastRead,
)
from app.service.weather import (
    FreshnessPolicyService,
    WeatherForecastService,
)


class WeatherForecastController(BaseController):
    service_class = WeatherForecastService
    read_schema = WeatherForecastRead
    list_schema = WeatherForecastListItem
    create_schema = WeatherForecastCreate
    query_schema = WeatherForecastQuery


class FreshnessPolicyController(BaseController):
    service_class = FreshnessPolicyService
    read_schema = FreshnessPolicyRead
    create_schema = FreshnessPolicyCreate
    update_schema = FreshnessPolicyUpdate
    query_schema = FreshnessPolicyQuery
