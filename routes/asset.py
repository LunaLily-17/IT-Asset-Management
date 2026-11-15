
from fastapi import APIRouter, HTTPException, status

from models.asset_request import (
    HardwareRegistrationRequest,
    HardwareRegistrationResponse
)

from services.asset_service import (
    register_hardware,
    get_hardware,
    list_hardware,
    DuplicateSerialError
)


router = APIRouter(
    prefix="/assets",
    tags=["Assets"]
)


@router.post(
    "",
    response_model=HardwareRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new IT infrastructure asset",
    description=(
        "Register a physical or virtual infrastructure asset. "
        "The server generates a unique internal ID. "
        "Duplicate identifiers are rejected. "
        "No employee assignment is created."
    ),
    responses={
        409: {"description": "Duplicate asset identifier"},
        422: {"description": "Invalid registration details"}
    }
)
def create_asset(request: HardwareRegistrationRequest):
    try:
        return register_hardware(request)

    except DuplicateSerialError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        ) from exc


@router.get(
    "",
    response_model=list[HardwareRegistrationResponse],
    summary="List registered IT assets"
)
def retrieve_assets():
    return list_hardware()


@router.get(
    "/{hardware_id}",
    response_model=HardwareRegistrationResponse,
    summary="Retrieve an IT asset by ID",
    responses={
        404: {"description": "Asset not found"}
    }
)
def retrieve_asset(hardware_id: str):
    asset = get_hardware(hardware_id)

    if asset is None:
        raise HTTPException(
            status_code=404,
            detail="Asset not found"
        )

    return asset
