from datetime import date, datetime, timezone
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NonBlank = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

HARDWARE_TYPES = Literal[
    "Laptop", "Desktop", "Server", "Printer", "Network Device",
    "Storage Device", "Virtual Machine", "Other Hardware",
]
SOFTWARE_TYPES = Literal[
    "Application", "Operating System", "Database", "Other Software",
]


class BaseRegistrationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: NonBlank = Field(max_length=150)
    location: NonBlank = Field(max_length=150)
    status: Literal["Available"] = "Available"
    purchase_date: date | None = None
    supplier: NonBlank | None = None
    cost: float | None = Field(default=None, ge=0, allow_inf_nan=False)


class HardwareRegistrationRequest(BaseRegistrationRequest):
    category: Literal["Hardware"]
    asset_type: HARDWARE_TYPES
    manufacturer: NonBlank | None = None
    model: NonBlank | None = None
    serial_number: NonBlank | None = None
    unique_identifier: NonBlank | None = None
    warranty_expiry: date | None = None

    @model_validator(mode="after")
    def validate_hardware(self):
        if not (self.serial_number or self.unique_identifier):
            raise ValueError("Hardware requires serial_number or unique_identifier")
        if self.asset_type != "Virtual Machine" and not (self.manufacturer and self.model):
            raise ValueError("Physical hardware requires manufacturer and model")
        return self


class SoftwareRegistrationRequest(BaseRegistrationRequest):
    category: Literal["Software"]
    asset_type: SOFTWARE_TYPES
    vendor: NonBlank
    product: NonBlank
    version: NonBlank
    installation_id: NonBlank

class AssetAssignmentRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    employee_id: str = Field(min_length=1)
    assignment_date: date | None = None
    due_date: date | None = None

    condition_at_handover: str | None = Field(
        default=None, max_length=500
    )
    notes: str | None = Field(
        default=None, max_length=2000
    )

    @model_validator(mode="after")
    def validate_assignment_dates(self):
        start = (
            self.assignment_date
            or datetime.now(timezone.utc).date()
        )

        if self.due_date and self.due_date < start:
            raise ValueError(
                "Due date cannot be before assignment date"
            )

        return self

AssetRegistrationRequest = Annotated[
    Union[HardwareRegistrationRequest, SoftwareRegistrationRequest],
    Field(discriminator="category"),
]


class BaseAssetResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    asset_id: str
    title: str
    location: str
    status: Literal["Available"]
    purchase_date: date | None = None
    supplier: str | None = None
    cost: float | None = None
    assigned_employee_id: None = None
    created_at: str
    updated_at: str


class HardwareAssetResponse(BaseAssetResponse):
    category: Literal["Hardware"]
    asset_type: HARDWARE_TYPES
    manufacturer: str | None = None
    model: str | None = None
    serial_number: str | None = None
    unique_identifier: str | None = None
    warranty_expiry: date | None = None


class SoftwareAssetResponse(BaseAssetResponse):
    category: Literal["Software"]
    asset_type: SOFTWARE_TYPES
    vendor: str
    product: str
    version: str
    installation_id: str

class AssetAssignmentResponse(BaseModel):
    assignment_id: str
    asset_id: str
    employee_id: str
    assignment_date: date
    due_date: date | None = None

    condition_at_handover: str | None = None
    notes: str | None = None

    status: Literal["Active"]
    assigned_by: str
    created_at: datetime

AssetRegistrationResponse = Annotated[
    Union[HardwareAssetResponse, SoftwareAssetResponse],
    Field(discriminator="category"),
]
