
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional


@dataclass
class HardwareAsset:
    hardware_id: str
    title: str
    product: Optional[str] = None

    category: str = "Physical"
    asset_type: str = "Other"
    manufacturer: Optional[str] = None
    serial_number: Optional[str] = None
    unique_identifier: Optional[str] = None

    location: str = "Headquarters"
    status: str = "Available"

    purchase_date: Optional[str] = None
    supplier: Optional[str] = None
    cost: Optional[float] = None
    warranty_expiry: Optional[str] = None

    assigned_employee_id: Optional[str] = None
    department: str = "General"

    created_at: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )

    def to_dict(self):
        return asdict(self)
