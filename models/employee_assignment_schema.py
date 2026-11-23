
from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel


class EmployeeAssignedAssetDetails(BaseModel):
    asset_id: str
    title: str
    category: str
    asset_type: str
    location: str
    status: str


class MyAssetAssignmentResponse(BaseModel):
    assignment_id: str
    assignment_date: date
    due_date: Optional[date] = None
    condition_at_handover: Optional[str] = None
    status: Literal["Active"]
    asset: EmployeeAssignedAssetDetails




class MyAssignedAssetResponse(BaseModel):
    asset_id: str
    title: str
    category: str