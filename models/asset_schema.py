from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, List, Dict, Any


class AssetStatus(str, Enum):
    AVAILABLE = "Available"
    ASSIGNED = "Assigned"
    DAMAGED = "Damaged"
    RETIRED = "Retired"


class DisposalMethod(str, Enum):
    RECYCLED = "Recycled"
    DESTROYED = "Destroyed"
    SOLD = "Sold"


@dataclass
class HardwareAsset:
    hardware_id: str                      # Key e.g., 'HW-10001'
    title: str
    product: str
    warranty_expiry: Optional[str] = None
    status: str = AssetStatus.AVAILABLE.value
    assigned_employee_id: Optional[str] = None
    department: str = "General"
    location: str = "Headquarters"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SoftwareLicence:
    licence_id: str                       # Key e.g., 'LIC-20001'
    software_name: str
    vendor: str
    total_seats: int
    assigned_employee_ids: List[str] = field(default_factory=list)
    licence_key: Optional[str] = None
    expiry_date: Optional[str] = None
    licence_type: str = "Subscription"
    department: str = "IT"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AssetRetirement:
    hardware_id: str
    disposal_method: str
    disposal_date: str
    data_wipe_verified: bool
    retired_by_user_id: str
    retired_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)