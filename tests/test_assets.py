
import copy
import json

import pytest
from fastapi.testclient import TestClient

from main import app
from database import db_json
from unittest.mock import patch

@pytest.fixture
def client(tmp_path, monkeypatch):
    """
    Purpose: Isolate each test using a temporary JSON database.
    Prevent tests from modifying the real asset inventory.
    """
    original_data = copy.deepcopy(db_json.DB)

    test_file = tmp_path / "test_itam_db.json"
    monkeypatch.setattr(db_json, "DB_FILE_PATH", test_file)

    db_json.DB.clear()
    db_json.DB.update({
        "hardware_assets": {},
        "software_licences": {},
        "asset_retirements": {}
    })

    db_json.save_db()

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        db_json.DB.clear()
        db_json.DB.update(original_data)


@pytest.fixture
def physical_asset():
    """Valid physical asset registration request."""
    return {
        "title": "Dell Latitude 5450",
        "product": "Latitude 5450",
        "category": "Physical",
        "asset_type": "Laptop",
        "manufacturer": "Dell",
        "serial_number": "SN-001",
        "location": "Leicester Office",
        "status": "Available"
    }


@pytest.fixture
def virtual_asset():
    """Valid virtual infrastructure asset request."""
    return {
        "title": "Development VM",
        "category": "Virtual",
        "asset_type": "Virtual Machine",
        "unique_identifier": "VM-001",
        "location": "Private Cloud",
        "status": "Available"
    }


# TC01 - Valid Physical Asset Registration
# Purpose: Verify that valid physical asset details create a record.
# Covers: AC1 - Successful registration with generated unique ID.
# Expected: HTTP 201, generated ID, no employee assignment.
def test_register_physical(client, physical_asset):
    response = client.post("/assets", json=physical_asset)

    assert response.status_code == 201
    assert response.json()["hardware_id"].startswith("HW-")
    assert response.json()["category"] == "Physical"
    assert response.json()["assigned_employee_id"] is None


# TC02 - Valid Virtual Asset Registration
# Purpose: Verify registration of a virtual machine without
# requiring a physical manufacturer, model or serial number.
# Covers: Physical/virtual asset support and AC1.
# Expected: HTTP 201 with virtual unique identifier.
def test_register_virtual(client, virtual_asset):
    response = client.post("/assets", json=virtual_asset)

    assert response.status_code == 201
    assert response.json()["category"] == "Virtual"
    assert response.json()["unique_identifier"] == "VM-001"
    assert response.json()["serial_number"] is None


# TC03-TC09 - Missing Mandatory Fields
# Purpose: Verify that required fields cannot be omitted.
# Covers: AC2 - Validation error and no inventory modification.
# Expected: HTTP 422 and zero registered assets.
#
# TC03: Missing asset title
# TC04: Missing category
# TC05: Missing location
# TC06: Missing initial status
# TC07: Missing physical manufacturer
# TC08: Missing physical model/product
# TC09: Missing physical serial number
@pytest.mark.parametrize(
    "field",
    [
        "title",
        "category",
        "location",
        "status",
        "manufacturer",
        "product",
        "serial_number"
    ]
)
def test_missing_required_field(client, physical_asset, field):
    physical_asset.pop(field)

    response = client.post("/assets", json=physical_asset)

    assert response.status_code == 422
    assert db_json.DB["hardware_assets"] == {}


# TC10 - Missing Virtual Unique Identifier
# Purpose: Verify that virtual assets require a unique identifier.
# Covers: Conditional mandatory fields and AC2.
# Expected: HTTP 422, no asset created.
def test_missing_virtual_identifier(client, virtual_asset):
    virtual_asset.pop("unique_identifier")

    response = client.post("/assets", json=virtual_asset)

    assert response.status_code == 422
    assert db_json.DB["hardware_assets"] == {}


# TC11 - Duplicate Physical Serial Number
# Purpose: Prevent two physical assets from using the same serial.
# Covers: Duplicate identifier business rule and AC3.
# Expected: First request 201, second 409, inventory unchanged.
def test_duplicate_serial(client, physical_asset):
    first = client.post("/assets", json=physical_asset)
    second = client.post("/assets", json=physical_asset)

    assert first.status_code == 201
    assert second.status_code == 409
    assert len(db_json.DB["hardware_assets"]) == 1


# TC12 - Duplicate Virtual Identifier
# Purpose: Prevent duplicate virtual machine identifiers.
# Covers: Identifier uniqueness business rule and AC3.
# Expected: First request 201, second 409, only one record.
def test_duplicate_virtual_identifier(client, virtual_asset):
    first = client.post("/assets", json=virtual_asset)
    second = client.post("/assets", json=virtual_asset)

    assert first.status_code == 201
    assert second.status_code == 409
    assert len(db_json.DB["hardware_assets"]) == 1


# TC13 - Invalid Category and Asset Type Combination
# Purpose: Ensure physical assets cannot use virtual-only types.
# Covers: Supported category/type validation business rule.
# Expected: HTTP 422, no record created.
def test_invalid_category_type(client, physical_asset):
    physical_asset["asset_type"] = "Virtual Machine"

    response = client.post("/assets", json=physical_asset)

    assert response.status_code == 422
    assert db_json.DB["hardware_assets"] == {}


# TC14 - Invalid Initial Status
# Purpose: Prevent newly registered assets starting as Assigned.
# Covers: Allowed onboarding status business rule.
# Expected: HTTP 422, no record created.
def test_invalid_status(client, physical_asset):
    physical_asset["status"] = "Assigned"

    response = client.post("/assets", json=physical_asset)

    assert response.status_code == 422
    assert db_json.DB["hardware_assets"] == {}


# TC15 - Client-Supplied ID or Employee Assignment
# Purpose: Prevent clients choosing internal IDs or silently
# creating employee assignments during registration.
# Covers: Server-generated ID and no-assignment business rules.
# Expected: HTTP 422, no inventory modification.
@pytest.mark.parametrize(
    "field,value",
    [
        ("hardware_id", "HW-CUSTOM"),
        ("assigned_employee_id", "EMP-001")
    ]
)
def test_forbidden_fields(client, physical_asset, field, value):
    physical_asset[field] = value

    response = client.post("/assets", json=physical_asset)

    assert response.status_code == 422
    assert db_json.DB["hardware_assets"] == {}


# TC16 - Unique Internal Asset ID Generation
# Purpose: Verify separate registrations generate different IDs.
# Covers: Unique internal asset ID business rule and AC1.
# Expected: Both 201, two different hardware IDs.
def test_unique_generated_ids(client, physical_asset):
    first = client.post("/assets", json=physical_asset)

    physical_asset["serial_number"] = "SN-002"
    second = client.post("/assets", json=physical_asset)

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["hardware_id"] != second.json()["hardware_id"]
    assert len(db_json.DB["hardware_assets"]) == 2


# TC17 - Retrieve Registered Asset
# Purpose: Verify that a newly registered asset is retrievable.
# Covers: AC4 - Retrieval API integration.
# Expected: HTTP 200 and correct asset details.
def test_retrieve_registered_asset(client, physical_asset):
    created = client.post("/assets", json=physical_asset)

    assert created.status_code == 201
    hardware_id = created.json()["hardware_id"]

    response = client.get(f"/assets/{hardware_id}")

    assert response.status_code == 200
    assert response.json()["hardware_id"] == hardware_id
    assert response.json()["serial_number"] == "SN-001"


# TC18 - JSON Persistence and Reload
# Purpose: Verify successful registrations survive database reload.
# Covers: In-memory inventory integration and AC4.
# Expected: Saved JSON contains the asset and GET returns it
# after reloading the database.
def test_json_persistence(client, physical_asset):
    created = client.post("/assets", json=physical_asset)

    assert created.status_code == 201
    hardware_id = created.json()["hardware_id"]

    with open(db_json.DB_FILE_PATH, encoding="utf-8") as f:
        saved_data = json.load(f)

    assert hardware_id in saved_data["hardware_assets"]

    db_json.DB.clear()
    db_json.load_db()

    response = client.get(f"/assets/{hardware_id}")

    assert response.status_code == 200
    assert response.json()["hardware_id"] == hardware_id


# TC19 - Optional Purchase Fields
# Purpose: Confirm registration succeeds without purchase details.
# Covers: Optional purchase date, supplier and cost requirements.
# Expected: HTTP 201 and optional fields set to None.
def test_optional_purchase_fields(client, physical_asset):
    response = client.post("/assets", json=physical_asset)

    assert response.status_code == 201
    assert response.json()["purchase_date"] is None
    assert response.json()["supplier"] is None
    assert response.json()["cost"] is None


# TC20 - Negative Purchase Cost
# Purpose: Reject invalid negative purchase costs.
# Covers: Boundary validation and data integrity.
# Expected: HTTP 422, no record created.
def test_negative_cost(client, physical_asset):
    physical_asset["cost"] = -100

    response = client.post("/assets", json=physical_asset)

    assert response.status_code == 422
    assert db_json.DB["hardware_assets"] == {}


# TC21 - Case-Insensitive Duplicate Identifier
# Purpose: Ensure serial numbers differing only in case
# cannot bypass duplicate detection.
# Covers: Identifier normalisation and AC3.
# Expected: HTTP 409 on second registration.
def test_case_insensitive_duplicate(client, physical_asset):
    first = client.post("/assets", json=physical_asset)

    physical_asset["serial_number"] = "sn-001"
    second = client.post("/assets", json=physical_asset)

    assert first.status_code == 201
    assert second.status_code == 409
    assert len(db_json.DB["hardware_assets"]) == 1


# TC22 - Retrieve Non-Existent Asset
# Purpose: Verify correct error handling for unknown IDs.
# Covers: Negative retrieval API testing.
# Expected: HTTP 404.
def test_unknown_asset(client):
    response = client.get("/assets/HW-UNKNOWN")

    assert response.status_code == 404


# TC23 - Whitespace-Only Mandatory Field
# Purpose: Prevent blank asset names from being accepted.
# Covers: Input validation and AC2.
# Expected: HTTP 422, no record created.
def test_whitespace_title(client, physical_asset):
    physical_asset["title"] = "   "

    response = client.post("/assets", json=physical_asset)

    assert response.status_code == 422
    assert db_json.DB["hardware_assets"] == {}


# TC24 - Cross-Category Duplicate Identifier
# Purpose: Prevent a physical serial number from being reused
# as a virtual asset identifier.
# Covers: Cross-category uniqueness and AC3.
# Expected: Second registration returns HTTP 409.
def test_cross_category_duplicate(
    client, physical_asset, virtual_asset
):
    physical_asset["serial_number"] = "SHARED-001"
    virtual_asset["unique_identifier"] = "SHARED-001"

    first = client.post("/assets", json=physical_asset)
    second = client.post("/assets", json=virtual_asset)

    assert first.status_code == 201
    assert second.status_code == 409
    assert len(db_json.DB["hardware_assets"]) == 1


from unittest.mock import patch

# TC25 - Database Save Failure
# Purpose: Verify that a failed database save does not
# leave an incomplete registration in memory.
# Covers: Failure handling and inventory integrity.
# Expected: OSError and no newly registered asset.

def test_database_save_failure(client, physical_asset):
    from services import asset_service
    from models.asset_request import HardwareRegistrationRequest

    request = HardwareRegistrationRequest(**physical_asset)

    with patch.object(
        asset_service,
        "save_db",
        side_effect=OSError("Simulated database failure")
    ):
        with pytest.raises(
            OSError,
            match="Simulated database failure"
        ):
            asset_service.register_hardware(request)

    assert db_json.DB["hardware_assets"] == {}


# TC26 - Unsupported Category
# Purpose: Reject categories not defined by the application.
# Covers: Supported category validation business rule.
# Expected: HTTP 422, no record created.
def test_invalid_category(client, physical_asset):
    physical_asset["category"] = "Furniture"

    response = client.post("/assets", json=physical_asset)

    assert response.status_code == 422
    assert db_json.DB["hardware_assets"] == {}


# TC27 - Unsupported Asset Type
# Purpose: Reject asset types not defined by the application.
# Covers: Supported asset type validation.
# Expected: HTTP 422, no record created.
def test_invalid_asset_type(client, physical_asset):
    physical_asset["asset_type"] = "Phone"

    response = client.post("/assets", json=physical_asset)

    assert response.status_code == 422
    assert db_json.DB["hardware_assets"] == {}


# TC28 - Optional Purchase Details Preserved
# Purpose: Verify optional purchase information is correctly
# stored and returned through the retrieval API.
# Covers: Data integrity and AC4.
# Expected: HTTP 201, then GET 200 with matching details.
def test_purchase_details_preserved(client, physical_asset):
    physical_asset.update({
        "purchase_date": "2026-11-01",
        "supplier": "Dell UK",
        "cost": 950.00,
        "warranty_expiry": "2029-11-01"
    })

    created = client.post("/assets", json=physical_asset)

    assert created.status_code == 201

    hardware_id = created.json()["hardware_id"]
    response = client.get(f"/assets/{hardware_id}")

    assert response.status_code == 200

    data = response.json()
    assert data["purchase_date"] == "2026-11-01"
    assert data["supplier"] == "Dell UK"
    assert data["cost"] == 950.00
    assert data["warranty_expiry"] == "2029-11-01"
