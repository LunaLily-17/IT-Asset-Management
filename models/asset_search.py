from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field

from models.asset_request import HARDWARE_TYPES, SOFTWARE_TYPES


class InventoryAssetBase(BaseModel):
    # Extra persistence fields (e.g. credentials) are intentionally not returned.
    model_config = ConfigDict(extra="ignore")
    asset_id: str
    title: str
    location: str
    status: str
    purchase_date: str | None = None
    supplier: str | None = None
    cost: float | None = None
    created_at: str
    updated_at: str


class HardwareInventoryResponse(InventoryAssetBase):
    category: Literal["Hardware"]
    asset_type: HARDWARE_TYPES
    manufacturer: str | None = None
    model: str | None = None
    serial_number: str | None = None
    unique_identifier: str | None = None
    warranty_expiry: str | None = None


class SoftwareInventoryResponse(InventoryAssetBase):
    category: Literal["Software"]
    asset_type: SOFTWARE_TYPES
    vendor: str
    product: str
    version: str
    # Installation identifiers and licensing secrets are not in discovery responses.


InventoryAssetResponse = Annotated[
    Union[HardwareInventoryResponse, SoftwareInventoryResponse],
    Field(discriminator="category"),
]
