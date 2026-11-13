from dataclasses import dataclass

from pydantic import BaseModel, EmailStr

@dataclass  
class Employee(BaseModel):
    employee_id: str
    full_name: str
    email: EmailStr
    department: str
    role: str = "Employee"
    is_active: bool = True
