"""Field types that many schemas use."""

from decimal import Decimal
from typing import Annotated

from pydantic import Field

Id = Annotated[int, Field(ge=1)]  # ID of a linked record
Name100 = Annotated[str, Field(min_length=1, max_length=100)]
Money = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)]
Quantity = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)]
Latitude = Annotated[Decimal, Field(ge=-90, le=90, max_digits=9, decimal_places=6)]
Longitude = Annotated[Decimal, Field(ge=-180, le=180, max_digits=9, decimal_places=6)]
Currency = Annotated[str, Field(pattern=r"^[A-Z]{3}$", description="ISO 4217 code, for example NGN")]
LanguageCode = Annotated[str, Field(pattern=r"^[a-z]{2,3}(-[A-Z]{2})?$", max_length=10)]
ClientReference = Annotated[str, Field(min_length=1, max_length=36, description="UUID from the offline client")]
Email = Annotated[str, Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=100)]
Phone = Annotated[str, Field(pattern=r"^\+[1-9]\d{6,14}$", description="E.164 format, for example +2348012345678")]
