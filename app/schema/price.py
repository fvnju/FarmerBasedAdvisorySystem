"""Schemas for price records."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.model.enums import PriceSource
from app.schema.common import ListQuery, ReadSchema
from app.schema.fields import Currency, Id, Name100

Price = Field(gt=0, max_digits=12, decimal_places=2)


class PriceRecordCreate(BaseModel):
    item_name: Name100
    unit: str = Field(min_length=1, max_length=20)
    price: Decimal = Price
    currency: Currency = "NGN"
    source: PriceSource
    priced_on: date
    region_id: Id | None = Field(None, description="Empty for a national price")
    farm_id: Id | None = Field(None, description="Necessary for a user quotation")
    recorded_by_id: Id | None = None


class PriceRecordUpdate(BaseModel):
    item_name: Name100 | None = None
    unit: str | None = Field(None, min_length=1, max_length=20)
    price: Decimal | None = Field(None, gt=0, max_digits=12, decimal_places=2)
    currency: Currency | None = None
    source: PriceSource | None = None
    priced_on: date | None = None
    region_id: Id | None = None
    farm_id: Id | None = None


class PriceRecordRead(ReadSchema):
    id: int
    item_name: str
    unit: str
    price: Decimal
    currency: str
    source: PriceSource
    priced_on: date
    region_id: int | None
    farm_id: int | None
    recorded_by_id: int | None
    created_at: datetime


class PriceRecordQuery(ListQuery):
    item_name: str | None = None
    source: PriceSource | None = None
    region_id: int | None = None
    farm_id: int | None = None
    currency: str | None = None
