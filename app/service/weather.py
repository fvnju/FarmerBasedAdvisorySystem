"""Business rules for weather forecasts and freshness policies."""

from app.core.exceptions import InvalidInputError
from app.model.enums import ForecastStatus
from app.model.weather import FreshnessPolicy, WeatherForecast
from app.repository.weather import FreshnessPolicyRepository, WeatherForecastRepository
from app.schema.common import Operation
from app.service.base import BaseService


class WeatherForecastService(BaseService[WeatherForecast]):
    repository_class = WeatherForecastRepository
    operations = frozenset(Operation) - {Operation.UPDATE}  # A forecast is a record of what the provider sent
    label = "Weather forecast"
    module = "weather"
    permissions = {
        Operation.CREATE: "weather.manage_forecasts",
        Operation.DELETE: "weather.manage_forecasts",
    }

    def validate(self, values, current):
        if values["status"] == ForecastStatus.FAILED:
            self._require_values(values, ["error_message"], "Give the error of the failed fetch.")
        if values["status"] == ForecastStatus.OK:
            self._require_values(values, ["payload"], "Give the forecast data.")
        valid_from, valid_to = values["valid_from"], values["valid_to"]
        if valid_from is not None and valid_to is not None and valid_to < valid_from:
            raise InvalidInputError("valid_to must not be before valid_from.", {"fields": ["valid_to"]})


class FreshnessPolicyService(BaseService[FreshnessPolicy]):
    repository_class = FreshnessPolicyRepository
    label = "Freshness policy"
    module = "weather"
    permissions = {
        Operation.CREATE: "weather.manage_policies",
        Operation.UPDATE: "weather.manage_policies",
        Operation.DELETE: "weather.manage_policies",
    }

    def validate(self, values, current):
        if values["requires_forecast"]:
            self._require_values(
                values,
                ["max_forecast_age_hours"],
                "Give the maximum forecast age for an action that needs a forecast.",
            )
