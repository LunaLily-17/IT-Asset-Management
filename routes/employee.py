from fastapi import APIRouter, Depends, HTTPException, Request, status

from models.employee_assignment_schema import (
    MyAssetAssignmentResponse,
    MyAssignedAssetResponse,
)

from models.employee_return_schema import (
    EmployeeReturnInformationResponse,
)

from services.asset_service import (
    get_employee_active_assignments,
    get_employee_assets,
    get_employee_return_information,
)

router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
)


def get_current_employee_id(request: Request) -> str:
    user = getattr(request.state, "user", None)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    if user.get("role") != "Employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employee access required",
        )

    employee_id = user.get("employee_id")

    if not isinstance(employee_id, str) or not employee_id.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authenticated employee identity",
        )

    return employee_id


@router.get(
    "/me/assignments",
    response_model=list[MyAssetAssignmentResponse],
    summary="View my active assigned assets",
    description=(
        "Returns active asset assignments belonging only to the "
        "authenticated employee. Employee identity is resolved "
        "from the verified caller context rather than supplied "
        "through query parameters or request data. Only permitted "
        "asset details are returned. This endpoint is read-only."
    ),
    responses={
        401: {
            "description": "Authentication required or invalid employee identity",
        },
        403: {
            "description": "Employee access required",
        },
    },
)
def get_my_assignments(
    employee_id: str = Depends(get_current_employee_id),
):
    try:
        return get_employee_active_assignments(employee_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    '/me/assets',
    response_model=list[MyAssignedAssetResponse],
    summary="View my assigned assets",
    description=(
        "Returns only the asset ID, title, and category "
        "of assets currently assigned to the authenticated employee."
    ),
)
def get_my_assets(
    employee_id: str = Depends(get_current_employee_id),
):
    try:
        return get_employee_assets(employee_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/me/assets/{asset_id}/return-information",
    response_model=EmployeeReturnInformationResponse,
    summary="View return information for my assigned asset",
    description=(
        "Returns the recorded return deadline and published "
        "return instructions for an asset belonging to the "
        "authenticated employee. This endpoint is read-only."
    ),
)
def get_my_asset_return_information(
    asset_id: str,
    employee_id: str = Depends(get_current_employee_id),
):
    try:
        return get_employee_return_information(
            employee_id=employee_id,
            asset_id=asset_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc