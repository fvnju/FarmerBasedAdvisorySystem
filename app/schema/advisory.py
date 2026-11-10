"""Schemas for advisory requests, responses, explanations, and citations."""

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field

from app.model.enums import (
    AccessMode,
    AdvisoryActionType,
    AdvisoryStatus,
    Affordability,
    ValidationStatus,
)
from app.schema.common import ListQuery, ReadSchema
from app.schema.fields import Id, LanguageCode, Money

# Advisory request


class AdvisoryRequestCreate(BaseModel):
    farmer_id: Id
    assisted_by_id: Id | None = Field(None, description="Necessary if access_mode is assisted")
    access_mode: AccessMode
    farm_id: Id | None = None
    crop_cycle_id: Id | None = None
    action_type: AdvisoryActionType
    question: str = Field(min_length=1, max_length=4000)


class AdvisoryRequestUpdate(BaseModel):
    farm_id: Id | None = None
    crop_cycle_id: Id | None = None
    action_type: AdvisoryActionType | None = None
    question: str | None = Field(None, min_length=1, max_length=4000)
    status: AdvisoryStatus | None = None
    missing_fields: list[str] | None = Field(None, description="Necessary if status is clarification_needed")
    referral_reason: str | None = Field(None, description="Necessary if status is referred")


class AdvisoryRequestRead(ReadSchema):
    id: int
    farmer_id: int
    assisted_by_id: int | None
    access_mode: AccessMode
    farm_id: int | None
    crop_cycle_id: int | None
    action_type: AdvisoryActionType
    question: str
    status: AdvisoryStatus
    missing_fields: Any | None
    referral_reason: str | None
    created_at: datetime
    updated_at: datetime


class AdvisoryRequestQuery(ListQuery):
    farmer_id: int | None = None
    assisted_by_id: int | None = None
    farm_id: int | None = None
    crop_cycle_id: int | None = None
    access_mode: AccessMode | None = None
    action_type: AdvisoryActionType | None = None
    status: AdvisoryStatus | None = None


# Advisory response


class AdvisoryResponseCreate(BaseModel):
    request_id: Id
    action: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    rule_ids: list[str | int] | None = None
    applicable_crop_stage: str | None = Field(None, max_length=50)
    suggested_timing: str | None = Field(None, max_length=255)
    resource_requirements: list[dict[str, Any]] | None = None
    affordability: Affordability = Affordability.UNDETERMINED
    estimated_cost: Money | None = None
    cost_assumptions: str | None = None
    weather_forecast_id: Id | None = None
    weather_is_stale: bool | None = None
    forecast_distance_km: float | None = Field(None, ge=0)
    unresolved_assumptions: list[str] | None = None
    uncertainty_notes: str | None = None
    expires_at: datetime | None = None


class AdvisoryResponseUpdate(BaseModel):
    action: str | None = Field(None, min_length=1)
    reason: str | None = Field(None, min_length=1)
    rule_ids: list[str | int] | None = None
    applicable_crop_stage: str | None = Field(None, max_length=50)
    suggested_timing: str | None = Field(None, max_length=255)
    resource_requirements: list[dict[str, Any]] | None = None
    affordability: Affordability | None = None
    estimated_cost: Money | None = None
    cost_assumptions: str | None = None
    weather_forecast_id: Id | None = None
    weather_is_stale: bool | None = None
    forecast_distance_km: float | None = Field(None, ge=0)
    unresolved_assumptions: list[str] | None = None
    uncertainty_notes: str | None = None
    expires_at: datetime | None = None


class AdvisoryResponseRead(ReadSchema):
    id: int
    request_id: int
    action: str
    reason: str
    rule_ids: Any | None
    applicable_crop_stage: str | None
    suggested_timing: str | None
    resource_requirements: Any | None
    affordability: Affordability
    estimated_cost: Decimal | None
    cost_assumptions: str | None
    weather_forecast_id: int | None
    weather_is_stale: bool | None
    forecast_distance_km: float | None
    unresolved_assumptions: Any | None
    uncertainty_notes: str | None
    expires_at: datetime | None
    created_at: datetime


class AdvisoryResponseQuery(ListQuery):
    request_id: int | None = None
    affordability: Affordability | None = None
    weather_is_stale: bool | None = None


# Advisory explanation


class AdvisoryExplanationCreate(BaseModel):
    response_id: Id
    language: LanguageCode = "en"
    text: str = Field(min_length=1)
    model_name: str = Field(min_length=1, max_length=100)
    model_version: str | None = Field(None, max_length=50)
    validation_status: ValidationStatus
    validation_notes: list[Any] | dict[str, Any] | None = None


class AdvisoryExplanationUpdate(BaseModel):
    validation_status: ValidationStatus | None = None
    validation_notes: list[Any] | dict[str, Any] | None = None
    is_current: bool | None = None


class AdvisoryExplanationRead(ReadSchema):
    id: int
    response_id: int
    language: str
    text: str
    model_name: str
    model_version: str | None
    validation_status: ValidationStatus
    validation_notes: Any | None
    is_current: bool
    created_at: datetime


class AdvisoryExplanationQuery(ListQuery):
    response_id: int | None = None
    language: str | None = None
    validation_status: ValidationStatus | None = None
    is_current: bool | None = None


# Advisory citation


class AdvisoryCitationCreate(BaseModel):
    explanation_id: Id
    chunk_id: Id
    similarity_score: float | None = None
    rank: int | None = Field(None, ge=1)


class AdvisoryCitationUpdate(BaseModel):
    similarity_score: float | None = None
    rank: int | None = Field(None, ge=1)


class AdvisoryCitationRead(ReadSchema):
    id: int
    explanation_id: int
    chunk_id: int
    similarity_score: float | None
    rank: int | None


class AdvisoryCitationQuery(ListQuery):
    explanation_id: int | None = None
    chunk_id: int | None = None
