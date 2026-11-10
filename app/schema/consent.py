"""Schemas for consent records. A record is never changed. To withdraw, insert a new record with granted false."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.model.enums import ConsentType
from app.schema.common import ListQuery, ReadSchema
from app.schema.fields import Id


class ConsentRecordCreate(BaseModel):
    user_id: Id
    consent_type: ConsentType
    granted: bool
    policy_version: str = Field(min_length=1, max_length=20)
    recorded_by_id: Id | None = Field(None, description="Extension agent who recorded it, if assisted")


class ConsentRecordRead(ReadSchema):
    id: int
    user_id: int
    consent_type: ConsentType
    granted: bool
    policy_version: str
    recorded_by_id: int | None
    created_at: datetime


class ConsentRecordQuery(ListQuery):
    user_id: int | None = None
    consent_type: ConsentType | None = None
    granted: bool | None = None
