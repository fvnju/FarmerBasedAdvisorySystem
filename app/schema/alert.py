"""Schemas for alerts."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.model.enums import AlertChannel, AlertStatus
from app.schema.common import ListQuery, ReadSchema
from app.schema.fields import Id


class AlertCreate(BaseModel):
    user_id: Id
    farm_id: Id | None = None
    response_id: Id | None = None
    weather_forecast_id: Id | None = None
    channel: AlertChannel
    title: str = Field(min_length=1, max_length=150)
    message: str = Field(min_length=1)
    dedupe_key: str = Field(min_length=1, max_length=150, description="For example '<farm>:<rule>:<date>'")
    scheduled_for: datetime
    expires_at: datetime | None = None


class AlertUpdate(BaseModel):
    channel: AlertChannel | None = None
    title: str | None = Field(None, min_length=1, max_length=150)
    message: str | None = Field(None, min_length=1)
    status: AlertStatus | None = None
    scheduled_for: datetime | None = None
    expires_at: datetime | None = None
    read_at: datetime | None = None


class AlertRead(ReadSchema):
    id: int
    user_id: int
    farm_id: int | None
    response_id: int | None
    weather_forecast_id: int | None
    channel: AlertChannel
    title: str
    message: str
    dedupe_key: str
    status: AlertStatus
    scheduled_for: datetime
    sent_at: datetime | None
    expires_at: datetime | None
    read_at: datetime | None
    created_at: datetime


class AlertQuery(ListQuery):
    user_id: int | None = None
    farm_id: int | None = None
    channel: AlertChannel | None = None
    status: AlertStatus | None = None
    unread: bool | None = None  # True: read_at is empty
