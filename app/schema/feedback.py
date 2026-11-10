"""Schemas for advisory feedback and field observations."""

from datetime import date, datetime

from pydantic import BaseModel, Field

from app.model.enums import FeedbackOutcome
from app.schema.common import ListQuery, ReadSchema
from app.schema.fields import ClientReference, Id

# Advisory feedback


class AdvisoryFeedbackCreate(BaseModel):
    response_id: Id
    outcome: FeedbackOutcome
    reason: str | None = Field(None, description="Necessary if the outcome is modified or rejected")
    action_date: date | None = None
    recorded_by_id: Id | None = None
    client_reference: ClientReference | None = None


class AdvisoryFeedbackUpdate(BaseModel):
    outcome: FeedbackOutcome | None = None
    reason: str | None = None
    action_date: date | None = None


class AdvisoryFeedbackRead(ReadSchema):
    id: int
    response_id: int
    outcome: FeedbackOutcome
    reason: str | None
    action_date: date | None
    recorded_by_id: int | None
    client_reference: str | None
    created_at: datetime


class AdvisoryFeedbackQuery(ListQuery):
    response_id: int | None = None
    outcome: FeedbackOutcome | None = None
    recorded_by_id: int | None = None


# Field observation


class FieldObservationCreate(BaseModel):
    crop_cycle_id: Id
    feedback_id: Id | None = None
    observed_on: date
    observation: str = Field(min_length=1)
    recorded_by_id: Id | None = None
    client_reference: ClientReference | None = None


class FieldObservationUpdate(BaseModel):
    feedback_id: Id | None = None
    observed_on: date | None = None
    observation: str | None = Field(None, min_length=1)
    is_verified: bool | None = Field(None, description="Set verified_by_id when this is true")
    verified_by_id: Id | None = None


class FieldObservationRead(ReadSchema):
    id: int
    crop_cycle_id: int
    feedback_id: int | None
    observed_on: date
    observation: str
    is_verified: bool
    verified_by_id: int | None
    recorded_by_id: int | None
    client_reference: str | None
    created_at: datetime


class FieldObservationQuery(ListQuery):
    crop_cycle_id: int | None = None
    feedback_id: int | None = None
    is_verified: bool | None = None
