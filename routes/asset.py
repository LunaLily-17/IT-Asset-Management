import os
from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, Query, status, Response, Depends, Request

from models.asset_request import (
    AssetRegistrationRequest,
    AssetRegistrationResponse,
    AssetAssignmentRequest,
    AssetAssignmentResponse,
)
from models.asset_search import InventoryAssetResponse
from services.asset_service import (
    DuplicateAssetIdentifierError,
    get_asset,
    search_assets,
    register_asset,
    assign_asset,
    get_current_asset_assignment,
    AssetAssignmentNotFound,
    AssetAssignmentConflict,
    EmployeeNotEligible,
    EmployeeNotFound,
)


router = APIRouter(prefix="/assets", tags=["Assets"])


@router.post("", response_model=AssetRegistrationResponse, status_code=status.HTTP_201_CREATED)
def create_asset(request: Annotated[AssetRegistrationRequest, Body()]):
    try:
        return register_asset(request)
    except DuplicateAssetIdentifierError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc



@router.get(
    "",
    response_model=list[InventoryAssetResponse],
    summary="Search and filter existing IT assets (read-only)",
    description=(
        "Filters combine with AND. category is an exact match; status is a "
        "case-insensitive exact match; location, manufacturer, model and search "
        "are case-insensitive substring matches. manufacturer/model only apply "
        "to hardware. Search scans asset ID, identifiers and non-secret "
        "descriptive fields. Results are sorted by asset_id, then paginated "
        "using offset and limit. X-Total-Count reports matches before pagination. "
        "No registration data is modified."
    ),
)
def get_assets(
    response: Response,
    category: Annotated[str | None, Query(pattern="^(Hardware|Software)$")] = None,
    status: Annotated[str | None, Query(min_length=1)] = None,
    location: Annotated[str | None, Query(min_length=1)] = None,
    manufacturer: Annotated[str | None, Query(min_length=1)] = None,
    model: Annotated[str | None, Query(min_length=1)] = None,
    search: Annotated[str | None, Query(min_length=1)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    records, total = search_assets(
        category=category, status=status, location=location,
        manufacturer=manufacturer, model=model, search=search,
        limit=limit, offset=offset,
    )
    response.headers["X-Total-Count"] = str(total)
    response.headers["X-Limit"] = str(limit)
    response.headers["X-Offset"] = str(offset)
    return records


@router.get(
    "/{asset_id}",
    response_model=InventoryAssetResponse,
    summary="Get permitted details for an existing asset",
    responses={404: {"description": "Asset not found"}},
)
def get_asset_by_id(asset_id: str):
    asset = get_asset(asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


def get_current_asset_manager(request: Request) -> str:
    """
    Authentication integration point.

    The future Authentication/ABAC implementation
    will provide a verified user through request.state.user.
    """

    user = getattr(request.state, "user", None)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )

    if user.get("role") != "Asset Manager":
        raise HTTPException(
            status_code=403,
            detail="Asset Manager role required",
        )

    user_id = user.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticated identity",
        )

    return user_id


@router.post(
    "/{asset_id}/assign",
    response_model=AssetAssignmentResponse,
    status_code=201,
    summary="Assign an available asset to an employee",
    responses={
        401: {"description": "Authentication required"},
        403: {"description": "Asset Manager access required"},
        404: {"description": "Asset or employee not found"},
        409: {"description": "Assignment conflict"},
        422: {"description": "Invalid assignment details"},
    },
)
def create_asset_assignment(
    asset_id: str,
    request: AssetAssignmentRequest,
    assigned_by: str = Depends(get_current_asset_manager),
):
    try:
        return assign_asset(
            asset_id=asset_id,
            request=request,
            assigned_by=assigned_by,
        )

    except (AssetAssignmentNotFound, EmployeeNotFound) as exc:
        raise HTTPException(
            status_code=404, detail=str(exc)
        ) from exc

    except (
        AssetAssignmentConflict,
        EmployeeNotEligible,
    ) as exc:
        raise HTTPException(
            status_code=409, detail=str(exc)
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=422, detail=str(exc)
        ) from exc


@router.get(
    "/{asset_id}/assignment",
    response_model=AssetAssignmentResponse,
    summary="Retrieve the current active asset assignment",
    responses={
        401: {"description": "Authentication required"},
        403: {"description": "Asset Manager access required"},
        404: {"description": "Active assignment not found"},
    },
)
def get_asset_assignment(
    asset_id: str,
    assigned_by: str = Depends(get_current_asset_manager),
):
    try:
        return get_current_asset_assignment(asset_id)

    except AssetAssignmentNotFound as exc:
        raise HTTPException(
            status_code=404, detail=str(exc)
        ) from exc
