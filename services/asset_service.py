
from uuid import uuid4

from database.db_json import DB, save_db
from models.asset_schema import HardwareAsset
from models.asset_request import HardwareRegistrationRequest


class DuplicateSerialError(Exception):
    """Raised when an asset identifier already exists."""
    pass


def normalize_identifier(value):
    if value is None:
        return None
    return value.strip().casefold()


def register_hardware(request: HardwareRegistrationRequest):
    """Validate, register and persist a new asset."""

    assets = DB["hardware_assets"]

    # Check every supplied identifier for uniqueness
    new_identifiers = {
        normalize_identifier(value)
        for value in (
            request.serial_number,
            request.unique_identifier
        )
        if value is not None
    }

    for existing in assets.values():
        existing_identifiers = {
            normalize_identifier(value)
            for value in (
                existing.get("serial_number"),
                existing.get("unique_identifier")
            )
            if value is not None
        }

        if new_identifiers & existing_identifiers:
            raise DuplicateSerialError(
                "An asset with this identifier already exists"
            )

    # Server-generated ID
    hardware_id = f"HW-{uuid4().hex.upper()}"

    while hardware_id in assets:
        hardware_id = f"HW-{uuid4().hex.upper()}"

    asset = HardwareAsset(
        hardware_id=hardware_id,
        title=request.title,
        product=request.product,
        category=request.category.value,
        asset_type=request.asset_type.value,
        manufacturer=request.manufacturer,
        serial_number=request.serial_number,
        unique_identifier=request.unique_identifier,
        location=request.location,
        status=request.status.value,

        purchase_date=(
            request.purchase_date.isoformat()
            if request.purchase_date else None
        ),
        supplier=request.supplier,
        cost=request.cost,
        warranty_expiry=(
            request.warranty_expiry.isoformat()
            if request.warranty_expiry else None
        ),

        assigned_employee_id=None
    )

    record = asset.to_dict()

    # Save only after validation and duplicate checking
    assets[hardware_id] = record

    try:
        save_db()
    except Exception:
        # Undo the insertion if persistence fails
        assets.pop(hardware_id, None)
        raise

    return record


def get_hardware(hardware_id: str):
    return DB["hardware_assets"].get(hardware_id)


def list_hardware():
    return list(DB["hardware_assets"].values())
