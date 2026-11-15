from uuid import uuid4
from database import db_json
from models.asset_request import HardwareRegistrationRequest, SoftwareRegistrationRequest
from models.asset_schema import HardwareAsset, SoftwareAsset
from copy import deepcopy
from datetime import datetime, timezone
from models.asset_request import AssetAssignmentRequest
from models.asset_schema import AssetAssignment



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



def search_assets(
    *,
    category: str | None = None,
    status: str | None = None,
    location: str | None = None,
    manufacturer: str | None = None,
    model: str | None = None,
    search: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[dict], int]:
    """AND filters; case-insensitive substring text matching; sorted, paginated snapshot.

    manufacturer/model apply only to hardware. The free-text search covers
    non-secret inventory metadata and identifiers in both asset categories.
    No mutation and no calls to save_db occur here.
    """
    def contains(value: object, needle: str | None) -> bool:
        return needle is None or needle.casefold() in str(value or "").casefold()

    with db_json.DB_LOCK:
        records = [
            record.copy()  # never expose mutable DB dictionaries
            for collection_name in ("hardware_assets", "software_assets")
            for record in db_json.DB[collection_name].values()
        ]

    matches: list[dict] = []
    for record in records:
        if category is not None and record.get("category") != category:
            continue
        if status is not None and str(record.get("status", "")).casefold() != status.casefold():
            continue
        if not contains(record.get("location"), location):
            continue
        if manufacturer is not None and (
            record.get("category") != "Hardware" or not contains(record.get("manufacturer"), manufacturer)
        ):
            continue
        if model is not None and (
            record.get("category") != "Hardware" or not contains(record.get("model"), model)
        ):
            continue
        if search is not None:
            fields = (
                "asset_id", "title", "asset_type", "location", "manufacturer",
                "model", "serial_number", "unique_identifier", "vendor",
                "product", "version", "installation_id",
            )
            if not any(contains(record.get(field), search) for field in fields):
                continue
        matches.append(record)

    matches.sort(key=lambda item: item["asset_id"])
    return matches[offset:offset + limit], len(matches)


class AssetAssignmentNotFound(Exception):
    pass


class EmployeeNotFound(Exception):
    pass


class AssetAssignmentConflict(Exception):
    pass


class EmployeeNotEligible(Exception):
    pass


def find_assignment_asset(asset_id: str):
    for collection in (
        "hardware_assets",
        "software_assets",
    ):
        asset = db_json.DB[collection].get(asset_id)

        if asset is not None:
            return asset

    return None


def find_active_assignment(asset_id: str):
    for assignment in db_json.DB[
        "asset_assignments"
    ].values():
        if (
            assignment["asset_id"] == asset_id
            and assignment["status"] == "Active"
        ):
            return assignment

    return None


def assign_asset(
    asset_id: str,
    request: AssetAssignmentRequest,
    assigned_by: str,
):
    if not assigned_by or not assigned_by.strip():
        raise PermissionError(
            "Authenticated Asset Manager is required"
        )

    with db_json.DB_LOCK:
        asset = find_assignment_asset(asset_id)

        if asset is None:
            raise AssetAssignmentNotFound(
                "Asset not found"
            )

        employee = db_json.DB["employees"].get(
            request.employee_id
        )

        if employee is None:
            raise EmployeeNotFound(
                "Employee not found"
            )

        if employee.get("status") != "Active":
            raise EmployeeNotEligible(
                "Employee is not eligible for assignment"
            )

        if (
            asset.get("status") != "Available"
            or asset.get("assigned_employee_id") is not None
            or find_active_assignment(asset_id) is not None
        ):
            raise AssetAssignmentConflict(
                "Asset is unavailable or already assigned"
            )

        now = datetime.now(timezone.utc)
        start_date = request.assignment_date or now.date()

        if (
            request.due_date is not None
            and request.due_date < start_date
        ):
            raise ValueError(
                "Due date cannot precede assignment date"
            )

        assignment_id = f"ASG-{uuid4().hex.upper()}"
        audit_id = f"AUD-{uuid4().hex.upper()}"

        assignment = AssetAssignment(
            assignment_id=assignment_id,
            asset_id=asset_id,
            employee_id=request.employee_id,
            assignment_date=start_date.isoformat(),
            due_date=(
                request.due_date.isoformat()
                if request.due_date else None
            ),
            condition_at_handover=(
                request.condition_at_handover
            ),
            notes=request.notes,
            status="Active",
            assigned_by=assigned_by,
            created_at=now.isoformat(),
        ).to_dict()

        # Preserve previous values for rollback.
        previous_asset = deepcopy(asset)

        previous_assignments = deepcopy(
            db_json.DB["asset_assignments"]
        )
        previous_audit = deepcopy(
            db_json.DB["audit_logs"]
        )

        try:
            db_json.DB[
                "asset_assignments"
            ][assignment_id] = assignment

            asset["status"] = "Assigned"
            asset["assigned_employee_id"] = (
                request.employee_id
            )
            asset["updated_at"] = now.isoformat()

            db_json.DB["audit_logs"][audit_id] = {
                "audit_id": audit_id,
                "event_type": "ASSET_ASSIGNED",
                "asset_id": asset_id,
                "assignment_id": assignment_id,
                "employee_id": request.employee_id,
                "performed_by": assigned_by,
                "timestamp": now.isoformat(),
            }

            db_json.save_db()

        except Exception:
            # Restore in-memory state if saving fails.
            asset.clear()
            asset.update(previous_asset)

            db_json.DB["asset_assignments"].clear()
            db_json.DB["asset_assignments"].update(
                previous_assignments
            )

            db_json.DB["audit_logs"].clear()
            db_json.DB["audit_logs"].update(
                previous_audit
            )

            raise

        return assignment


def get_current_asset_assignment(asset_id: str):
    with db_json.DB_LOCK:
        asset = find_assignment_asset(asset_id)

        if asset is None:
            raise AssetAssignmentNotFound(
                "Asset not found"
            )

        assignment = find_active_assignment(asset_id)

        if assignment is None:
            raise AssetAssignmentNotFound(
                "No active assignment found"
            )

        return deepcopy(assignment)
