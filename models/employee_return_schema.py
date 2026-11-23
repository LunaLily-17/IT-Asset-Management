from datetime import date
from pydantic import BaseModel


class EmployeeReturnInformationResponse(BaseModel):
    asset_id: str
    assignment_id: str
    return_due_date: date | None
    due_date_recorded: bool
    return_instructions: list[str]