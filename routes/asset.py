from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, Query, status

from models.asset_request import AssetRegistrationRequest, AssetRegistrationResponse
from services.asset_service import (
    DuplicateAssetIdentifierError,
    get_asset,
    list_assets,
    register_asset,
)

router = APIRouter(prefix="/assets", tags=["Assets"])


@router.post("", response_model=AssetRegistrationResponse, status_code=status.HTTP_201_CREATED)
def create_asset(request: Annotated[AssetRegistrationRequest, Body()]):
    try:
        return register_asset(request)
    except DuplicateAssetIdentifierError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("", response_model=list[AssetRegistrationResponse])
def get_assets(category: Annotated[str | None, Query(pattern="^(Hardware|Software)$")] = None):
    return list_assets(category)


@router.get("/{asset_id}", response_model=AssetRegistrationResponse)
def get_asset_by_id(asset_id: str):
    asset = get_asset(asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset
