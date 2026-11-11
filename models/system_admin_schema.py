from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


#user account management

class AccountStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class UserCreate(BaseModel):
    display_name: str = Field(..., min_length=2, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    department: Optional[str] = None
    contact: Optional[str] = None


class UserUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=2, max_length=100)
    department: Optional[str] = None
    contact: Optional[str] = None


class UserResponse(BaseModel):
    user_id: int
    display_name: str
    username: str
    email: EmailStr
    department: Optional[str] = None
    contact: Optional[str] = None
    status: AccountStatus


#roles and permissions management

class Role(str, Enum):
    ASSET_MANAGER = "Asset Manager"
    EMPLOYEE = "Employee"
    AUDITOR = "Auditor"
    SYSTEM_ADMINISTRATOR = "System Administrator"


class RoleAssignment(BaseModel):
    roles: list[Role] = Field(..., min_length=1)


class PermissionUpdate(BaseModel):
    permissions: list[str] = Field(..., min_length=1)


class RoleResponse(BaseModel):
    role_id: str
    role_name: Role
    permissions: list[str]


#asset category and reference data management

class AssetCategoryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=20)
    description: Optional[str] = None


class AssetCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class AssetCategoryResponse(BaseModel):
    category_id: int
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool


class ReferenceValueResponse(BaseModel):
    value: str