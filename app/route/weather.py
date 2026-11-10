"""Routes for weather forecasts, freshness policies."""

from app.controller.weather import (
    FreshnessPolicyController,
    WeatherForecastController,
)
from app.route.factory import build_crud_router

routers = [
    build_crud_router(WeatherForecastController, prefix="/weather-forecasts", tag="Weather forecasts"),
    build_crud_router(FreshnessPolicyController, prefix="/freshness-policies", tag="Freshness policies"),
]
