
from datetime import date
from enum import Enum
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator
)


class AssetCategory(str, Enum):
    PHYSICAL = "Physical"
    VIRTUAL = "Virtual"


class HardwareType(str, Enum):
    LAPTOP = "Laptop"
    DESKTOP = "Desktop"
    SERVER = "Server"
    PRINTER = "Printer"
    OTHER = "Other"
    VIRTUAL_MACHINE = "Virtual Machine"


class RegistrationStatus(str, Enum):
    AVAILABLE = "Available"


class HardwareRegistrationRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )

    title: str = Field(min_length=1)
    category: AssetCategory
    asset_type: HardwareType
    location: str = Field(min_length=1)
    status: RegistrationStatus

    product: Optional[str] = None
    manufacturer: Optional[str] = None
    serial_number: Optional[str] = None
    unique_identifier: Optional[str] = None

    purchase_date: Optional[date] = None
    supplier: Optional[str] = None
    cost: Optional[float] = Field(
        default=None,
        ge=0,
        allow_inf_nan=False
    )
    warranty_expiry: Optional[date] = None

    @model_validator(mode="after")
    def validate_asset_details(self):

        physical_types = {
            HardwareType.LAPTOP,
            HardwareType.DESKTOP,
            HardwareType.SERVER,
            HardwareType.PRINTER,
            HardwareType.OTHER
        }

        if self.category == AssetCategory.PHYSICAL:
            if self.asset_type not in physical_types:
                raise ValueError(
                    "Invalid asset type for physical asset"
                )

            if not self.manufacturer:
                raise ValueError(
                    "Manufacturer is required for physical assets"
                )

            if not self.product:
                raise ValueError(
                    "Model/product is required for physical assets"
                )

            if not self.serial_number:
                raise ValueError(
                    "Serial number is required for physical assets"
                )

        elif self.category == AssetCategory.VIRTUAL:
            if self.asset_type != HardwareType.VIRTUAL_MACHINE:
                raise ValueError(
                    "Invalid asset type for virtual asset"
                )

            if not self.unique_identifier:
                raise ValueError(
                    "Unique identifier is required for virtual assets"
                )

        # Optional identifiers must not be blank
        for name in ("serial_number", "unique_identifier"):
            value = getattr(self, name)
            if value is not None and not value.strip():
                raise ValueError(
                    f"{name} cannot be blank"
                )

        return self


class HardwareRegistrationResponse(BaseModel):
    hardware_id: str
    title: str
    category: AssetCategory
    asset_type: HardwareType
    location: str
    status: RegistrationStatus

    product: Optional[str] = None
    manufacturer: Optional[str] = None
    serial_number: Optional[str] = None
    unique_identifier: Optional[str] = None

    purchase_date: Optional[date] = None
    supplier: Optional[str] = None
    cost: Optional[float] = None
    warranty_expiry: Optional[date] = None

    assigned_employee_id: Optional[str] = None
    department: str = "General"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
