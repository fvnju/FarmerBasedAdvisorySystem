"""Schemas for farms, farm resources, and soil records. An empty field means "unknown"."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.model.enums import DataProvenance, ResourceType, WaterAccess
from app.schema.common import ListQuery, ReadSchema
from app.schema.fields import (
    ClientReference,
    Currency,
    Id,
    Latitude,
    Longitude,
    Money,
    Name100,
    Quantity,
)

Area = Field(None, gt=0, max_digits=10, decimal_places=2, description="Hectares")


# Farm


class FarmCreate(BaseModel):
    owner_id: Id
    region_id: Id | None = None
    name: Name100
    latitude: Latitude | None = None
    longitude: Longitude | None = None
    location_description: str | None = Field(None, max_length=255)
    cultivated_area_ha: Decimal | None = Area
    water_access: WaterAccess | None = None
    budget_min: Money | None = None
    budget_max: Money | None = None
    currency: Currency = "NGN"
    client_reference: ClientReference | None = None


class FarmUpdate(BaseModel):
    owner_id: Id | None = None
    region_id: Id | None = None
    name: Name100 | None = None
    latitude: Latitude | None = None
    longitude: Longitude | None = None
    location_description: str | None = Field(None, max_length=255)
    cultivated_area_ha: Decimal | None = Area
    water_access: WaterAccess | None = None
    budget_min: Money | None = None
    budget_max: Money | None = None
    currency: Currency | None = None


class FarmRead(ReadSchema):
    id: int
    owner_id: int
    region_id: int | None
    name: str
    latitude: Decimal | None
    longitude: Decimal | None
    location_description: str | None
    cultivated_area_ha: Decimal | None
    water_access: WaterAccess | None
    budget_min: Decimal | None
    budget_max: Decimal | None
    currency: str
    client_reference: str | None
    created_at: datetime
    updated_at: datetime


class FarmQuery(ListQuery):
    owner_id: int | None = None
    region_id: int | None = None
    water_access: WaterAccess | None = None


# Farm resource


class FarmResourceCreate(BaseModel):
    farm_id: Id
    resource_type: ResourceType
    name: Name100
    is_available: bool
    quantity: Quantity | None = None
    unit: str | None = Field(None, max_length=20)
    notes: str | None = None


class FarmResourceUpdate(BaseModel):
    resource_type: ResourceType | None = None
    name: Name100 | None = None
    is_available: bool | None = None
    quantity: Quantity | None = None
    unit: str | None = Field(None, max_length=20)
    notes: str | None = None


class FarmResourceRead(ReadSchema):
    id: int
    farm_id: int
    resource_type: ResourceType
    name: str
    is_available: bool
    quantity: Decimal | None
    unit: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class FarmResourceQuery(ListQuery):
    farm_id: int | None = None
    resource_type: ResourceType | None = None
    is_available: bool | None = None


# Soil record

SoilValue = Field(None, max_digits=12, decimal_places=4)


class SoilRecordCreate(BaseModel):
    farm_id: Id
    property_name: str = Field(min_length=1, max_length=50, description="For example 'ph' or 'nitrogen'")
    value: Decimal | None = SoilValue
    value_text: str | None = Field(None, max_length=100)
    unit: str | None = Field(None, max_length=20)
    provenance: DataProvenance
    measured_on: date | None = None
    source_note: str | None = Field(None, max_length=255)


class SoilRecordUpdate(BaseModel):
    property_name: str | None = Field(None, min_length=1, max_length=50)
    value: Decimal | None = SoilValue
    value_text: str | None = Field(None, max_length=100)
    unit: str | None = Field(None, max_length=20)
    provenance: DataProvenance | None = None
    measured_on: date | None = None
    source_note: str | None = Field(None, max_length=255)


class SoilRecordRead(ReadSchema):
    id: int
    farm_id: int
    property_name: str
    value: Decimal | None
    value_text: str | None
    unit: str | None
    provenance: DataProvenance
    measured_on: date | None
    source_note: str | None
    created_at: datetime
    updated_at: datetime


class SoilRecordQuery(ListQuery):
    farm_id: int | None = None
    property_name: str | None = None
    provenance: DataProvenance | None = None
