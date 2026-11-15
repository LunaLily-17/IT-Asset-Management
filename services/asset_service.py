"""Registration rules for both asset categories in one service file."""
from uuid import uuid4

from database import db_json
from models.asset_request import HardwareRegistrationRequest, SoftwareRegistrationRequest
from models.asset_schema import HardwareAsset, SoftwareAsset


class DuplicateAssetIdentifierError(Exception):
    pass


def _normalise(value: str | None) -> str | None:
    return value.strip().casefold() if value is not None else None


def _generate_asset_id(prefix: str, collection: dict) -> str:
    while True:
        candidate = f"{prefix}-{uuid4().hex[:12].upper()}"
        if candidate not in collection:
            return candidate


def register_hardware(request: HardwareRegistrationRequest) -> dict:
    with db_json.DB_LOCK:
        collection = db_json.DB["hardware_assets"]
        identifiers = {
            _normalise(value)
            for value in (request.serial_number, request.unique_identifier)
            if value is not None
        }
        for existing in collection.values():
            existing_ids = {
                _normalise(value)
                for value in (existing.get("serial_number"), existing.get("unique_identifier"))
                if value is not None
            }
            if identifiers & existing_ids:
                raise DuplicateAssetIdentifierError("Hardware identifier already registered")

        asset_id = _generate_asset_id("HW", collection)
        record = HardwareAsset(
            asset_id=asset_id,
            **request.model_dump(),
        ).to_dict()
        collection[asset_id] = record
        try:
            db_json.save_db()
        except Exception:
            collection.pop(asset_id, None)
            raise
        return record


def register_software(request: SoftwareRegistrationRequest) -> dict:
    with db_json.DB_LOCK:
        collection = db_json.DB["software_assets"]
        installation_id = _normalise(request.installation_id)
        if any(_normalise(asset.get("installation_id")) == installation_id
               for asset in collection.values()):
            raise DuplicateAssetIdentifierError("Software installation identifier already registered")

        asset_id = _generate_asset_id("SW", collection)
        record = SoftwareAsset(
            asset_id=asset_id,
            **request.model_dump(),
        ).to_dict()
        collection[asset_id] = record
        try:
            db_json.save_db()
        except Exception:
            collection.pop(asset_id, None)
            raise
        return record


def register_asset(request: HardwareRegistrationRequest | SoftwareRegistrationRequest) -> dict:
    if isinstance(request, HardwareRegistrationRequest):
        return register_hardware(request)
    if isinstance(request, SoftwareRegistrationRequest):
        return register_software(request)
    raise TypeError("Unsupported asset request")


def get_asset(asset_id: str) -> dict | None:
    with db_json.DB_LOCK:
        if asset_id.startswith("HW-"):
            return db_json.DB["hardware_assets"].get(asset_id)
        if asset_id.startswith("SW-"):
            return db_json.DB["software_assets"].get(asset_id)
        return None


def list_assets(category: str | None = None) -> list[dict]:
    with db_json.DB_LOCK:
        if category == "Hardware":
            return list(db_json.DB["hardware_assets"].values())
        if category == "Software":
            return list(db_json.DB["software_assets"].values())
        return list(db_json.DB["hardware_assets"].values()) + list(db_json.DB["software_assets"].values())
