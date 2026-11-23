from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from typing import Optional

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(kw_only=True)
class BaseAsset:
    asset_id: str
    title: str
    category: str
    asset_type: str
    location: str
    status: str
    purchase_date: date | None = None
    supplier: str | None = None
    cost: float | None = None
    assigned_employee_id: None = None
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict:
        record = asdict(self)
        if record["purchase_date"] is not None:
            record["purchase_date"] = record["purchase_date"].isoformat()
        return record


@dataclass(kw_only=True)
class HardwareAsset(BaseAsset):
    manufacturer: str | None = None
    model: str | None = None
    serial_number: str | None = None
    unique_identifier: str | None = None
    warranty_expiry: date | None = None

    def to_dict(self) -> dict:
        record = super().to_dict()
        if record["warranty_expiry"] is not None:
            record["warranty_expiry"] = record["warranty_expiry"].isoformat()
        return record


@dataclass(kw_only=True)
class SoftwareAsset(BaseAsset):
    vendor: str
    product: str
    version: str
    installation_id: str

@dataclass
class AssetAssignment:
    assignment_id: str
    asset_id: str
    employee_id: str

    assignment_date: str
    due_date: Optional[str]

    condition_at_handover: Optional[str]
    notes: Optional[str]

    status: str
    assigned_by: str
    created_at: str

    def to_dict(self):
        return asdict(self)
