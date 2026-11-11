from fastapi import APIRouter

from models.system_admin_schema import (
    UserCreate,
    UserUpdate,
    RoleAssignment,
    PermissionUpdate,
    AssetCategoryCreate,
    AssetCategoryUpdate
)

from services import system_admin_service as service


router = APIRouter(
    prefix="/api/v1/admin",
    tags=["System Administrator"]
)


#user management

@router.post("/users", status_code=201)
def create_user(data: UserCreate):
    return service.create_user(data)


@router.get("/users")
def get_all_users():
    return service.get_all_users()


@router.get("/users/{user_id}")
def get_user(user_id: int):
    return service.get_user(user_id)


@router.patch("/users/{user_id}")
def update_user(user_id: int, data: UserUpdate):
    return service.update_user(user_id, data)


@router.post("/users/{user_id}/deactivation")
def deactivate_user(user_id: int):
    return service.deactivate_user(user_id)


#roles and permissions management

@router.get("/roles")
def get_all_roles():
    return service.get_all_roles()


@router.get("/roles/{role_id}/permissions")
def get_role_permissions(role_id: str):
    return service.get_role_permissions(role_id)


@router.put("/users/{user_id}/roles")
def assign_user_roles(user_id: int, data: RoleAssignment):
    return service.assign_user_roles(user_id, data.roles)


@router.put("/roles/{role_id}/permissions")
def update_role_permissions(role_id: str, data: PermissionUpdate):
    return service.update_role_permissions(
        role_id,
        data.permissions
    )


#asset categories and reference values management

@router.get("/reference-data/asset-categories")
def get_asset_categories():
    return service.get_asset_categories()


@router.post(
    "/reference-data/asset-categories",
    status_code=201
)
def create_asset_category(data: AssetCategoryCreate):
    return service.create_asset_category(data)


@router.patch("/reference-data/asset-categories/{category_id}")
def update_asset_category(
    category_id: int,
    data: AssetCategoryUpdate
):
    return service.update_asset_category(category_id, data)


@router.get("/reference-data/asset-statuses")
def get_asset_statuses():
    return service.get_asset_statuses()