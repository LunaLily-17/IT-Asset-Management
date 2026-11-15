import pytest
from database import db_json


# TC01 - Valid Physical Asset Registration
# Purpose: Verify a valid physical asset category is accepted.
# Technique: Black-box / Category Partition
# Expected: HTTP 201 with a generated hardware ID.
def test_valid_physical_asset(client, physical_asset):
    response = client.post("/assets", json=physical_asset)

    assert response.status_code == 201
    assert response.json()["hardware_id"].startswith("HW-")


# TC02 - Valid Virtual Asset Registration
# Purpose: Verify a valid virtual asset category is accepted.
# Technique: Black-box / Category Partition
# Expected: HTTP 201 with the unique virtual identifier.
def test_valid_virtual_asset(client, virtual_asset):
    response = client.post("/assets", json=virtual_asset)

    assert response.status_code == 201
    assert response.json()["unique_identifier"] == "VM-001"


# TC03-TC09 - Missing Mandatory Fields
# Purpose: Verify invalid input partitions are rejected.
# Technique: Black-box / Category Partition
# Expected: HTTP 422 with no inventory modification.
@pytest.mark.parametrize(
    "field",
    [
        "title",           # TC03
        "category",        # TC04
        "location",        # TC05
        "status",          # TC06
        "manufacturer",    # TC07
        "product",         # TC08
        "serial_number"    # TC09
    ]
)
def test_missing_required_field(client, physical_asset, field):
    physical_asset.pop(field)

    response = client.post("/assets", json=physical_asset)

    assert response.status_code == 422

# TC10 - Missing Virtual Unique Identifier
# Purpose: Verify that virtual assets require a unique identifier.
# Covers: Conditional mandatory fields and AC2.
# Expected: HTTP 422, no asset created.
def test_missing_virtual_identifier(client, virtual_asset):
    virtual_asset.pop("unique_identifier")

    response = client.post("/assets", json=virtual_asset)

    assert response.status_code == 422
    assert db_json.DB["hardware_assets"] == {}


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
