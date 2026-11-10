"""Schemas for crop cycles."""

from datetime import date, datetime

from pydantic import BaseModel, Field

from app.model.enums import CropCycleStatus
from app.schema.common import ListQuery, ReadSchema
from app.schema.fields import Id


class CropCycleCreate(BaseModel):
    farm_id: Id
    crop_id: Id
    season_label: str | None = Field(None, max_length=50)
    planting_date: date | None = None
    crop_stage: str | None = Field(None, max_length=50)
    status: CropCycleStatus = CropCycleStatus.ACTIVE
    ended_on: date | None = None


class CropCycleUpdate(BaseModel):
    crop_id: Id | None = None
    season_label: str | None = Field(None, max_length=50)
    planting_date: date | None = None
    crop_stage: str | None = Field(None, max_length=50)
    status: CropCycleStatus | None = None
    ended_on: date | None = None


class CropCycleRead(ReadSchema):
    id: int
    farm_id: int
    crop_id: int
    season_label: str | None
    planting_date: date | None
    crop_stage: str | None
    stage_updated_at: datetime | None
    status: CropCycleStatus
    ended_on: date | None
    created_at: datetime
    updated_at: datetime


class CropCycleQuery(ListQuery):
    farm_id: int | None = None
    crop_id: int | None = None
    status: CropCycleStatus | None = None
